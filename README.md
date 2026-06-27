# 衡安AI合规通 (HengAn AI Compliance Pass)

> 面向中国出海企业的免费AI合规自检工具

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)](https://voguecs86.github.io/hengan-compliance-check/)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

## 一句话介绍

**5分钟了解你的AI产品是否需要在2026年8月2日前完成EU AI Act合规 -- 完全免费，无需注册。**

## 为什么需要这个工具？

欧盟AI法案（EU AI Act）第50条将于 **2026年8月2日** 全面强制执行。只要你的产品向欧盟用户展示AI生成内容（图片/视频/音频），你就属于"部署者"，须承担合规义务。

| 项目 | 截止日期 |
|------|----------|
| EU AI透明度行为准则签署 | **2026年7月22日** |
| AI合成内容标识强制 | **2026年8月2日** |
| C2PA水印强制 | 2026年12月2日 |
| 最高罚款 | 1500万欧元 或 全球年营业额3% |

## 功能介绍

### 1. AI合规需求自检
5道核心问题，3分钟完成评估：
- 你的产品是否使用AI生成内容？
- 是否有欧盟用户？
- 目前是否有AI内容标识？
- 是否已签署行为准则？
- 是否有内容溯源记录？

**结果分级：高风险 / 中风险 / 低风险，附带具体行动清单。**

### 2. C2PA技术速查
即用型技术方案汇总：
- C2PA签名工具 (c2patool) -- CLI
- c2pa-python -- Python绑定
- c2pa-js -- 浏览器端库
- EU AI官方标签图标
- 行为准则签署模板

全部基于 Apache 2.0/MIT 开源许可，零成本可商用。

### 3. 5周合规冲刺路线图
从今天到8月2日的每周行动清单，确保按时完成合规准备。

### 4. 零成本启动
- GitHub Pages 免费托管
- 纯前端HTML/CSS/JS
- 无需服务器、无需数据库、无需注册

## 快速开始

### 在线使用
访问 **[https://voguecs86.github.io/hengan-compliance-check/](https://voguecs86.github.io/hengan-compliance-check/)**

### 本地运行
```bash
git clone https://github.com/voguecs86/hengan-compliance-check.git
cd hengan-compliance-check
# 直接用浏览器打开 index.html
open index.html
```

无需任何构建工具或依赖。

## 项目结构

```
hengan-compliance-check/
  index.html    -- 主页面（合规自检工具 + 方案介绍 + FAQ）
  README.md     -- 本文件
  LICENSE       -- MIT 许可证
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | 纯 HTML/CSS/JS |
| 部署 | GitHub Pages |
| C2PA | c2pa-js（浏览器端，计划集成） |
| 成本 | 0元 |

## 路线图

| 阶段 | 时间 | 内容 |
|------|------|------|
| MVP v1.0 | 2026-07-01 | 合规自检工具 + 技术速查表 + 行为准则指南 |
| v1.1 | 2026-07-08 | EU AI Act合规手册中文版 + 客户案例 |
| v1.2 | 2026-07-15 | C2PA签名工具集成 + 合规报告生成器 |
| v2.0 | 2026-07-22 | ProductHunt正式发布 + 多语言支持 |

## 贡献

欢迎提交 Issue 和 Pull Request。

当前阶段以内容完善和功能增强为主，主要方向：
- 多语言支持（英文版）
- C2PA签名功能集成
- 合规报告自动生成
- 更多行业场景案例

## 关于衡安AI

衡安AI是一个聚焦AI前沿尚未被商品化能力的创业项目，致力于为中国本地企业和出海企业提供零成本AI赋能方案。

## 免责声明

本工具为信息参考工具，不构成法律建议。具体合规决策请咨询专业法律顾问。

## 许可证

MIT License

## 联系方式

- 邮箱：hengan-ai@proton.me
- GitHub Issues：[提交问题](https://github.com/voguecs86/hengan-compliance-check/issues)
