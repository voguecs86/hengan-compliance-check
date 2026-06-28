#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
衡安AI合规通 -- C2PA签名工具 (Pro版核心功能)

为单张图片嵌入C2PA Content Credentials manifest，声明AI生成内容来源。
满足EU AI Act第50条机器可读标注要求。

功能:
  1. 自签名ES256证书生成（零成本demo/测试用）
  2. 单图C2PA签名（声明AI生成来源）
  3. 签名验证（读取已签名图片的manifest）
  4. 批量签名（多图一次处理）
  5. 自定义manifest（用户自定义assertions）

零成本方案: 全部基于开源c2pa-python库(Apache 2.0) + cryptography库
生产环境: 需替换为正式C2PA信任锚证书（需从C2PA授权CA获取）

使用示例:
  # 生成demo证书
  python c2pa_signer.py --generate-cert

  # 签名单张图片（使用demo证书）
  python c2pa_signer.py sign input.jpg output_signed.jpg

  # 签名并声明为AI生成
  python c2pa_signer.py sign input.jpg output_signed.jpg --ai-generated

  # 验证已签名图片
  python c2pa_signer.py verify signed_image.jpg

  # 批量签名
  python c2pa_signer.py batch ./input_dir ./output_dir --ai-generated

作者: ES-01 (衡安AI执行专员)
版本: v1.0
日期: 2026-06-28
许可: Apache 2.0 (与c2pa-python一致)
"""

import argparse
import json
import os
import sys
import datetime
import glob
import shutil
from pathlib import Path

# ============================================================
# 证书生成模块 (零成本demo/测试用)
# ============================================================

def generate_self_signed_cert(cert_dir: str = None, force: bool = False):
    """
    生成C2PA签名所需的证书链：CA根证书 + 由CA签发的叶子签名证书。

    C2PA要求签名证书由信任锚CA签发（不能是自签名）。
    本函数创建一个本地CA根证书 + 由该CA签发的叶子证书，用于demo/测试。
    CA根证书会被添加到c2pa Settings的user_anchors中，使签名证书被信任。

    生产环境需替换为C2PA授权CA签发的正式证书。
    C2PA信任锚获取方式: https://c2pa.org/practice/trust-list/

    Args:
        cert_dir: 证书保存目录，默认为脚本所在目录下的 certs/
        force: 是否强制重新生成

    Returns:
        (leaf_cert_path, leaf_key_path, ca_cert_path) 叶子证书、私钥、CA根证书路径
    """
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.backends import default_backend
    except ImportError:
        print("[错误] 需要安装 cryptography 库: pip install cryptography")
        sys.exit(1)

    if cert_dir is None:
        cert_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs")

    ca_cert_path = os.path.join(cert_dir, "hengan_ca_root.pem")
    leaf_cert_path = os.path.join(cert_dir, "hengan_es256_certs.pem")
    leaf_key_path = os.path.join(cert_dir, "hengan_es256_private.key")

    # 如果证书已存在且不强制重新生成，直接返回路径
    if all(os.path.exists(p) for p in [ca_cert_path, leaf_cert_path, leaf_key_path]) and not force:
        print(f"[信息] CA根证书已存在: {ca_cert_path}")
        print(f"[信息] 叶子签名证书已存在: {leaf_cert_path}")
        print(f"[信息] 叶子私钥已存在: {leaf_key_path}")
        print("[警告] 这是本地demo证书，仅用于开发/测试。生产环境需使用C2PA信任锚签发的正式证书。")
        return leaf_cert_path, leaf_key_path, ca_cert_path

    os.makedirs(cert_dir, exist_ok=True)

    print("[信息] 生成衡安AI合规通demo证书链（CA根证书 + 叶子签名证书）...")

    # === 第1步：生成CA根证书 ===
    ca_private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())

    ca_subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "HengAn AI Compliance Pass Demo CA"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "HengAn AI"),
        x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Hunan"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Hengyang"),
    ])

    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_subject)
        .issuer_name(ca_subject)
        .public_key(ca_private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3650))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=1),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_cert_sign=True,
                crl_sign=True,
                key_agreement=False,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .sign(ca_private_key, hashes.SHA256(), default_backend())
    )

    # 保存CA根证书
    ca_cert_pem = ca_cert.public_bytes(serialization.Encoding.PEM)
    with open(ca_cert_path, "wb") as f:
        f.write(ca_cert_pem)

    # 保存CA私钥（仅用于签发叶子证书，不用于日常签名）
    ca_key_pem = ca_private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()
    )
    ca_key_path = os.path.join(cert_dir, "hengan_ca_private.key")
    with open(ca_key_path, "wb") as f:
        f.write(ca_key_pem)

    # === 第2步：生成叶子签名证书（由CA签发）===
    leaf_private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())

    leaf_subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "HengAn AI Compliance Pass Signer"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "HengAn AI"),
        x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
    ])

    leaf_cert = (
        x509.CertificateBuilder()
        .subject_name(leaf_subject)
        .issuer_name(ca_subject)  # 由CA签发！
        .public_key(leaf_private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_cert_sign=False,
                key_agreement=False,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
            critical=False,
        )
        .sign(ca_private_key, hashes.SHA256(), default_backend())  # 用CA私钥签发
    )

    # 保存叶子证书（包含完整链：叶子证书 + CA证书）
    leaf_cert_pem = leaf_cert.public_bytes(serialization.Encoding.PEM)
    cert_chain_pem = leaf_cert_pem + ca_cert_pem  # 叶子证书 + CA证书 = 完整证书链
    with open(leaf_cert_path, "wb") as f:
        f.write(cert_chain_pem)

    # 保存叶子私钥
    leaf_key_pem = leaf_private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()
    )
    with open(leaf_key_path, "wb") as f:
        f.write(leaf_key_pem)

    print(f"[成功] CA根证书已保存: {ca_cert_path}")
    print(f"[成功] 叶子签名证书已保存: {leaf_cert_path}（含完整证书链）")
    print(f"[成功] 叶子私钥已保存: {leaf_key_path}")
    print("[信息] 证书链结构: CA根证书 -> 叶子签名证书")
    print("[警告] 这是本地demo证书链，仅用于开发/测试！")
    print("[警告] 生产环境需从C2PA授权CA获取信任锚签发的正式证书。")
    print("[提示] C2PA信任锚获取: https://c2pa.org/practice/trust-list/")

    return leaf_cert_path, leaf_key_path, ca_cert_path


# ============================================================
# AI生成内容Manifest模板
# ============================================================

AI_GENERATED_MANIFEST_TEMPLATE = {
    "claim_generator_info": [{
        "name": "HengAn AI Compliance Pass",
        "version": "1.0.0",
    }],
    "format": "image/jpeg",  # 会根据输入文件自动调整
    "title": "AI Generated Image - HengAn AI Compliance Pass Signed",
    "assertions": [
        {
            "label": "c2pa.actions",
            "data": {
                "actions": [
                    {
                        "action": "c2pa.created",
                        "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia"
                    }
                ]
            }
        },
        {
            "label": "cawg.training-mining",
            "data": {
                "entries": {
                    "cawg.ai_inference": {
                        "use": "notAllowed"
                    },
                    "cawg.ai_generative_training": {
                        "use": "notAllowed"
                    }
                }
            }
        }
    ]
}

# 非AI生成但经过AI处理的manifest模板
AI_ENHANCED_MANIFEST_TEMPLATE = {
    "claim_generator_info": [{
        "name": "HengAn AI Compliance Pass",
        "version": "1.0.0",
    }],
    "format": "image/jpeg",
    "title": "AI Enhanced Image - HengAn AI Compliance Pass Signed",
    "assertions": [
        {
            "label": "c2pa.actions",
            "data": {
                "actions": [
                    {
                        "action": "c2pa.edited",
                        "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/algorithmicEnhancement"
                    }
                ]
            }
        }
    ]
}


# ============================================================
# 核心签名功能
# ============================================================

def get_format_from_path(filepath: str) -> str:
    """根据文件扩展名判断MIME类型。"""
    ext = os.path.splitext(filepath)[1].lower()
    format_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".avif": "image/avif",
        ".tif": "image/tiff",
        ".tiff": "image/tiff",
    }
    return format_map.get(ext, "image/jpeg")


def sign_image(
    input_path: str,
    output_path: str,
    cert_path: str,
    key_path: str,
    ca_cert_path: str = None,
    manifest_json: str = None,
    ai_generated: bool = True,
    ai_enhanced: bool = False,
    custom_title: str = None,
    tsa_url: str = "http://timestamp.digicert.com",
    verbose: bool = False
):
    """
    为单张图片签名C2PA manifest。

    Args:
        input_path: 输入图片文件路径
        output_path: 输出签名图片文件路径
        cert_path: PEM叶子签名证书文件路径（含完整证书链）
        key_path: PEM叶子私钥文件路径
        ca_cert_path: CA根证书路径（用于配置user_anchor信任）
        manifest_json: 自定义manifest JSON字符串（可选）
        ai_generated: 是否声明为AI生成内容（默认True）
        ai_enhanced: 是否声明为AI增强内容（默认False）
        custom_title: 自定义标题（可选）
        tsa_url: 时间戳服务URL（默认DigiCert）
        verbose: 是否显示详细信息

    Returns:
        True if signing successful, False otherwise
    """
    try:
        import c2pa
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.backends import default_backend
    except ImportError as e:
        missing = str(e).split("'")[-2] if "'" in str(e) else str(e)
        print(f"[错误] 缺少依赖库: {missing}")
        if missing == "c2pa":
            print("[提示] 安装c2pa-python: pip install c2pa-python")
        elif missing.startswith("cryptography"):
            print("[提示] 安装cryptography: pip install cryptography")
        return False

    # 检查输入文件
    if not os.path.exists(input_path):
        print(f"[错误] 输入文件不存在: {input_path}")
        return False

    # 读取证书和私钥
    try:
        with open(cert_path, "rb") as f:
            certs = f.read()
        with open(key_path, "rb") as f:
            key_data = f.read()
    except FileNotFoundError as e:
        print(f"[错误] 证书/私钥文件不存在: {e}")
        return False

    # 构建manifest
    format_str = get_format_from_path(input_path)

    if manifest_json:
        # 用户自定义manifest
        manifest_def = json.loads(manifest_json)
    elif ai_enhanced:
        # AI增强内容
        manifest_def = dict(AI_ENHANCED_MANIFEST_TEMPLATE)
        manifest_def["format"] = format_str
    else:
        # AI生成内容（默认）
        manifest_def = dict(AI_GENERATED_MANIFEST_TEMPLATE)
        manifest_def["format"] = format_str

    if custom_title:
        manifest_def["title"] = custom_title

    if verbose:
        print(f"[信息] 输入文件: {input_path}")
        print(f"[信息] 输出文件: {output_path}")
        print(f"[信息] 图片格式: {format_str}")
        print(f"[信息] Manifest标题: {manifest_def.get('title', 'N/A')}")
        print(f"[信息] 数字来源类型: {manifest_def['assertions'][0]['data']['actions'][0]['digitalSourceType']}")

    # 定义签名回调函数
    def callback_signer_es256(data: bytes) -> bytes:
        """ES256签名回调函数。"""
        private_key = serialization.load_pem_private_key(
            key_data,
            password=None,
            backend=default_backend()
        )
        signature = private_key.sign(
            data,
            ec.ECDSA(hashes.SHA256())
        )
        return signature

    # 构建信任配置（将CA根证书添加为user_anchor）
    cert_pem_str = certs.decode('utf-8')

    # 读取CA根证书
    ca_cert_pem_str = None
    if ca_cert_path and os.path.exists(ca_cert_path):
        with open(ca_cert_path, "rb") as f:
            ca_cert_pem_str = f.read().decode('utf-8')

    try:
        trust_config = {}
        if ca_cert_pem_str:
            # 将CA根证书添加为user_anchor（保留SDK内置信任锚）
            trust_config["user_anchors"] = ca_cert_pem_str
        else:
            # 如果没有CA证书，使用allowed_list绕过（仅测试环境）
            trust_config["allowed_list"] = cert_pem_str

        settings = c2pa.Settings.from_dict({
            "trust": trust_config,
            "verify": {
                "verify_trust": True,
                "verify_timestamp_trust": True
            }
        })
    except Exception as e:
        # 如果Settings.from_dict不可用，回退到默认Context
        if verbose:
            print(f"[警告] Settings配置失败（回退到默认）: {e}")
        settings = None

    # 执行签名
    try:
        if settings:
            context = c2pa.Context(settings)
        else:
            context = c2pa.Context()

        with context:
            with c2pa.Signer.from_callback(
                callback_signer_es256,
                c2pa.C2paSigningAlg.ES256,
                cert_pem_str,
                tsa_url
            ) as signer:
                manifest_json_str = json.dumps(manifest_def)
                with c2pa.Builder(manifest_json_str, context) as builder:
                    builder.sign_file(
                        input_path,
                        output_path,
                        signer
                    )

        print(f"[成功] 签名完成: {output_path}")
        print(f"[信息] 图片已嵌入C2PA Content Credentials manifest")

        if verbose:
            # 验证签名结果
            verify_image(output_path, verbose=True, cert_path=cert_path)

        return True

    except Exception as e:
        print(f"[错误] 签名失败: {e}")
        return False


def verify_image(image_path: str, verbose: bool = False, cert_path: str = None, ca_cert_path: str = None):
    """
    验证已签名图片的C2PA manifest。

    Args:
        image_path: 已签名图片文件路径
        verbose: 是否显示详细manifest信息
        cert_path: 叶子签名证书路径（用于allowed_list信任）
        ca_cert_path: CA根证书路径（用于user_anchor信任）

    Returns:
        manifest_store JSON dict if found, None otherwise
    """
    try:
        import c2pa
    except ImportError:
        print("[错误] 需要安装c2pa-python: pip install c2pa-python")
        return None

    if not os.path.exists(image_path):
        print(f"[错误] 文件不存在: {image_path}")
        return None

    format_str = get_format_from_path(image_path)

    # 构建信任配置（优先使用CA根证书作为user_anchor）
    settings = None
    try:
        trust_config = {}
        if ca_cert_path and os.path.exists(ca_cert_path):
            with open(ca_cert_path, "rb") as f:
                ca_cert_pem = f.read().decode('utf-8')
            trust_config["user_anchors"] = ca_cert_pem
        elif cert_path and os.path.exists(cert_path):
            with open(cert_path, "rb") as f:
                cert_pem = f.read().decode('utf-8')
            trust_config["allowed_list"] = cert_pem

        if trust_config:
            settings = c2pa.Settings.from_dict({"trust": trust_config})
    except Exception:
        pass

    try:
        context = c2pa.Context(settings) if settings else c2pa.Context()
        with context:
            with open(image_path, "rb") as file:
                with c2pa.Reader(format_str, file, context=context) as reader:
                    manifest_json = reader.json()
                    manifest_store = json.loads(manifest_json)

        if verbose:
            print(f"[信息] C2PA Manifest Store 详情:")
            print(json.dumps(manifest_store, indent=2, ensure_ascii=False))
        else:
            # 简要信息
            if "active_manifest" in manifest_store:
                active_id = manifest_store["active_manifest"]
                if active_id in manifest_store.get("manifests", {}):
                    active = manifest_store["manifests"][active_id]
                    print(f"[信息] 有效Manifest: {active.get('title', 'N/A')}")
                    print(f"[信息] 生成器: {active.get('claim_generator', 'N/A')}")

                    # 检查AI相关assertions
                    assertions = active.get("assertions", [])
                    for assertion in assertions:
                        label = assertion.get("label", "")
                        if "c2pa.actions" in label:
                            actions = assertion.get("data", {}).get("actions", [])
                            for action in actions:
                                ds_type = action.get("digitalSourceType", "")
                                if "trainedAlgorithmicMedia" in ds_type:
                                    print("[信息] 内容声明: AI生成内容")
                                elif "algorithmicEnhancement" in ds_type:
                                    print("[信息] 内容声明: AI增强内容")
                        if "cawg.training-mining" in label:
                            entries = assertion.get("data", {}).get("entries", {})
                            print(f"[信息] AI训练数据使用声明: {entries}")
            else:
                print("[信息] 图片不含C2PA manifest")

            validation = manifest_store.get("validation_status", [])
            if validation:
                print(f"[信息] 验证状态: {validation}")

        return manifest_store

    except Exception as e:
        print(f"[警告] 验证失败: {e}")
        print("[提示] 自签名证书的manifest验证状态将为Invalid（非C2PA信任锚）")
        print("[提示] 这是正常的demo行为，生产环境需使用C2PA信任锚证书")
        return None


def batch_sign(
    input_dir: str,
    output_dir: str,
    cert_path: str,
    key_path: str,
    ai_generated: bool = True,
    ai_enhanced: bool = False,
    tsa_url: str = "http://timestamp.digicert.com",
    verbose: bool = False
):
    """
    批量签名目录下的所有图片。

    Args:
        input_dir: 输入图片目录
        output_dir: 输出签名图片目录
        cert_path: PEM证书文件路径
        key_path: PEM私钥文件路径
        ai_generated: 是否声明为AI生成内容
        ai_enhanced: 是否声明为AI增强内容
        tsa_url: 时间戳服务URL
        verbose: 是否显示详细信息

    Returns:
        (成功数, 失败数)
    """
    supported_extensions = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".tif", ".tiff"}

    os.makedirs(output_dir, exist_ok=True)

    success_count = 0
    fail_count = 0

    for filename in os.listdir(input_dir):
        ext = os.path.splitext(filename)[1].lower()
        if ext not in supported_extensions:
            continue

        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        print(f"\n--- 签名: {filename} ---")
        result = sign_image(
            input_path=input_path,
            output_path=output_path,
            cert_path=cert_path,
            key_path=key_path,
            ai_generated=ai_generated,
            ai_enhanced=ai_enhanced,
            tsa_url=tsa_url,
            verbose=verbose
        )

        if result:
            success_count += 1
        else:
            fail_count += 1

    print(f"\n[汇总] 成功: {success_count}, 失败: {fail_count}")
    return success_count, fail_count


# ============================================================
# CLI入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="衡安AI合规通 - C2PA签名工具 (Pro版核心功能)",
        epilog="EU AI Act第50条合规: 8月2日硬截止 | 证书获取: https://c2pa.org/practice/trust-list/",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # generate-cert 子命令
    cert_parser = subparsers.add_parser(
        "generate-cert",
        help="生成demo自签名ES256证书（零成本测试用，生产需替换为C2PA信任锚）"
    )
    cert_parser.add_argument(
        "--cert-dir", default=None,
        help="证书保存目录（默认: 脚本目录/certs/）"
    )
    cert_parser.add_argument(
        "--force", action="store_true",
        help="强制重新生成证书"
    )

    # sign 子命令
    sign_parser = subparsers.add_parser(
        "sign",
        help="为单张图片签名C2PA manifest"
    )
    sign_parser.add_argument("input", help="输入图片文件路径")
    sign_parser.add_argument("output", help="输出签名图片文件路径")
    sign_parser.add_argument(
        "--cert", default=None,
        help="PEM证书文件路径（默认: 脚本目录/certs/hengan_es256_certs.pem）"
    )
    sign_parser.add_argument(
        "--key", default=None,
        help="PEM私钥文件路径（默认: 脚本目录/certs/hengan_es256_private.key）"
    )
    sign_parser.add_argument(
        "--ca", default=None,
        help="CA根证书路径（默认: 脚本目录/certs/hengan_ca_root.pem，用于信任配置）"
    )
    sign_parser.add_argument(
        "--ai-generated", action="store_true", default=True,
        help="声明为AI生成内容（默认启用）"
    )
    sign_parser.add_argument(
        "--ai-enhanced", action="store_true",
        help="声明为AI增强内容（而非AI生成）"
    )
    sign_parser.add_argument(
        "--title", default=None,
        help="自定义manifest标题"
    )
    sign_parser.add_argument(
        "--manifest", default=None,
        help="自定义manifest JSON字符串"
    )
    sign_parser.add_argument(
        "--tsa-url", default="http://timestamp.digicert.com",
        help="时间戳服务URL（默认: DigiCert）"
    )
    sign_parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="显示详细签名信息"
    )

    # verify 子命令
    verify_parser = subparsers.add_parser(
        "verify",
        help="验证已签名图片的C2PA manifest"
    )
    verify_parser.add_argument("input", help="已签名图片文件路径")
    verify_parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="显示完整manifest JSON"
    )

    # batch 子命令
    batch_parser = subparsers.add_parser(
        "batch",
        help="批量签名目录下所有图片"
    )
    batch_parser.add_argument("input_dir", help="输入图片目录")
    batch_parser.add_argument("output_dir", help="输出签名图片目录")
    batch_parser.add_argument(
        "--cert", default=None,
        help="PEM证书文件路径（默认: 脚本目录/certs/）"
    )
    batch_parser.add_argument(
        "--key", default=None,
        help="PEM私钥文件路径（默认: 脚本目录/certs/）"
    )
    batch_parser.add_argument(
        "--ai-generated", action="store_true", default=True,
        help="声明为AI生成内容（默认启用）"
    )
    batch_parser.add_argument(
        "--ai-enhanced", action="store_true",
        help="声明为AI增强内容"
    )
    batch_parser.add_argument(
        "--tsa-url", default="http://timestamp.digicert.com",
        help="时间戳服务URL"
    )
    batch_parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="显示详细签名信息"
    )

    # --generate-cert 快捷选项（顶层）
    parser.add_argument(
        "--generate-cert", action="store_true",
        help="快捷生成demo自签名证书"
    )

    args = parser.parse_args()

    # 顶层快捷选项
    if args.generate_cert:
        generate_self_signed_cert(force=False)
        return

    if not args.command:
        parser.print_help()
        print("\n快速开始:")
        print("  1. python c2pa_signer.py generate-cert          # 生成demo证书")
        print("  2. python c2pa_signer.py sign input.jpg output.jpg --ai-generated  # 签名图片")
        print("  3. python c2pa_signer.py verify output.jpg      # 验证签名")
        print("\nEU AI Act合规: https://voguecs86.github.io/hengan-compliance-check/")
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_cert_dir = os.path.join(script_dir, "certs")
    default_cert = os.path.join(default_cert_dir, "hengan_es256_certs.pem")
    default_key = os.path.join(default_cert_dir, "hengan_es256_private.key")
    default_ca = os.path.join(default_cert_dir, "hengan_ca_root.pem")

    if args.command == "generate-cert":
        leaf_cert, leaf_key, ca_cert = generate_self_signed_cert(
            cert_dir=args.cert_dir,
            force=args.force
        )

    elif args.command == "sign":
        cert_path = args.cert or default_cert
        key_path = args.key or default_key
        ca_path = args.ca or default_ca

    # 如果证书不存在，自动生成
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print("[信息] 证书不存在，检查是否有C2PA官方测试证书...")
        # 优先使用C2PA官方测试证书（在certs/test_fixtures/目录下）
        test_cert = os.path.join(default_cert_dir, "test_fixtures", "es256_certs.pem")
        test_key = os.path.join(default_cert_dir, "test_fixtures", "es256_private.key")
        if os.path.exists(test_cert) and os.path.exists(test_key):
            print("[信息] 使用C2PA官方测试证书（demo模式）")
            cert_path = test_cert
            key_path = test_key
            ca_path = None  # 官方测试证书自带信任链，不需要额外CA
        else:
            print("[信息] 无C2PA官方测试证书，自动生成demo证书链...")
            leaf_cert, leaf_key, ca_cert = generate_self_signed_cert(cert_dir=default_cert_dir, force=True)
            cert_path = leaf_cert
            key_path = leaf_key
            ca_path = ca_cert

        success = sign_image(
            input_path=args.input,
            output_path=args.output,
            cert_path=cert_path,
            key_path=key_path,
            ca_cert_path=ca_path,
            manifest_json=args.manifest,
            ai_generated=args.ai_generated,
            ai_enhanced=args.ai_enhanced,
            custom_title=args.title,
            tsa_url=args.tsa_url,
            verbose=args.verbose
        )

        if not success:
            sys.exit(1)

    elif args.command == "verify":
        result = verify_image(args.input, verbose=args.verbose)
        if result is None:
            print("[警告] 验证未返回有效结果")

    elif args.command == "batch":
        cert_path = args.cert or default_cert
        key_path = args.key or default_key

        if not os.path.exists(cert_path) or not os.path.exists(key_path):
            print("[信息] 证书不存在，自动生成demo证书...")
            cert_path, key_path = generate_self_signed_cert(cert_dir=default_cert_dir)

        batch_sign(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            cert_path=cert_path,
            key_path=key_path,
            ai_generated=args.ai_generated,
            ai_enhanced=args.ai_enhanced,
            tsa_url=args.tsa_url,
            verbose=args.verbose
        )


if __name__ == "__main__":
    main()
