# MacLean — 隐私优先、AI 决策的 macOS 磁盘审计 Skill

**当前源码 v1.4.0｜历史安装 ZIP 最新 v1.3.1｜MIT 许可证**

它帮助 AI 识别值得进一步讨论的**技术缓存与构建产物**，不以“找到大文件就删除”为目标。

**AI 负责价值判断**：哪些文件值得清理、损失与重建成本、是否影响现有任务、应满足哪些执行条件。

**脚本负责技术边界**：只读取经过授权的技术目标，进行空间测量、进程及路径安全检查、拒绝危险计划，以及在用户逐项授权后执行。脚本不负责决定“应该删除什么”。

## 隐私承诺

- 默认 Privacy Safe 只测量已知技术缓存叶目录；不对整个 `~`、`~/Library` 或 `~/Developer` 进行递归扫描。
- 不因 Mac 的 Full Disk Access 权限而访问 Mail、Messages、CloudDocs、MobileSync、AddressBook、FaceTime、Keychains、照片、浏览器个人资料等。
- 默认 JSON 采用匿名目标编号与技术分类，不含完整路径、机器名、用户账号或原始进程命令行；**控制台收据、错误和用户主动启用的详情输出仍需避免公开分享**。
- `complete_within_policy=true` 仅表示允许的技术目标已完成测量，不是 Home 全盘覆盖。

## 使用流程

1. **v1.4.0 源码**：从可信仓库检出完整的 [`skill/macos-disk-auditor/`](skill/macos-disk-auditor/) 目录，检查其中的 `SKILL.md`，使用原版 `scripts/verify_bundle.py --json` 验证清单后，按兼容平台支持的方式安装；内部 manifest 不能独自证明发布者身份。
2. **历史 ZIP**：仓库现有的 `macos-disk-auditor-v1.3.1.zip` 仍可通过 [SHA-256](artifacts/SHA256SUMS.txt) 校验，但安装的是 **v1.3.1，不是 v1.4.0**。本次仅同步新版源码，没有声称发布 v1.4.0 ZIP。安装 Skill **并不自动授权访问 Mac**。
3. 通过已独立授权的 Mac 连接器执行原版 `verify_bundle.py` 和只读审计，先不要申请实际清理。
4. AI 结合测量值、进程保护、可再生性、离线需求与风险进行分析。
5. 用户决定是否继续了解精确路径、查看计划或批准清理。`--plan` 默认仅预览，绝不执行删除；`--apply` 需要**新的、明确的逐项批准**及本机交互终端输入 `DELETE`，社区验收禁止使用。

## 验收证据与限制

v1.4.0 原版源码在 2026-10-17 经一台授权 Mac 完成 17 文件 manifest 校验和 **67/67 项临时 HOME 夹具自测**，没有清理用户真实缓存；该证据不等同于新版本完整 G0–G7 发布验收。

v1.3.0 于 2026-10-16 在**一台** Mac mini（macOS 26.5.2，Python 3.14.7）通过 G0–G7：manifest 17/17、自测 53/53、Home 策略内 20/20、Library 策略内 4/4。未执行真实文件清理，不能据此宣称适配所有 macOS / 连接器。

## 社区发布状态

**本项目已按 [MIT](LICENSE) 许可证开源**，版权声明为 2026 cookyecat。仓库内 Skill 源码与 manifest 已更新为 v1.4.0；历史 v1.3.0／v1.3.1 安装 ZIP 及各自校验和保持不变，分别进行完整性检查。原 G0–G7 验收适用于历史 v1.3.0。见 [v1.4.0 源码同步说明](docs/RELEASE-NOTES-v1.4.0.md)。


- [安装与运行](docs/INSTALLATION.md)
- [隐私策略](PRIVACY.md)
- [安全策略](SECURITY.md)
- [AI 和执行器分工](docs/AI-EXECUTOR-CONTRACT.md)
- [兼容性说明](docs/COMPATIBILITY.md)
- [发布前待办](docs/RELEASE-CHECKLIST.md)

**v1.3.1 修复 [Issue #1](https://github.com/cookyecat/maclean-skill/issues/1)**；安装后请重新验证 G0–G7。
