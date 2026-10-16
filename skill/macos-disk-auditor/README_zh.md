# macOS Disk Auditor & Safe Cleanup v1.3.1

Privacy-First Community Edition。无需 sudo、不调整隐私权限、不读取个人资料内容。默认仅测量已知技术缓存叶子目录的已分配空间，不递归扫描整个 Home/Library。AI 根据用户目标、缓存再生性、依赖和风险分析是否值得清理；脚本负责不可绕过的隐私保护、计划预演以及经人工批准后的安全执行。工具不会自行决定什么“值得删除”。

## 安装与原版验证
安装 ZIP 到 ChatGPT Skill 后，新开会话读取实际当前 Skill 与 `references/execution-contract.md`，通过已经授权的 Mac MCP Gateway 连接 Mac。仅允许在私有临时目录部署 Skill 并写入日志、报告；不需要读取 MobileSync、CloudDocs、TCC、AddressBook、FaceTime、Knowledge、FileProvider、Mail、Messages、Keychains 等隐私目录。

```bash
python3 scripts/verify_bundle.py --json
# 将报告目录创建为当前用户专用，权限 0700
REPORT_DIR=$(mktemp -d)
python3 scripts/audit_session.py --scope home --output-dir "$REPORT_DIR"
python3 scripts/audit_session.py --scope library --output-dir "$REPORT_DIR"
python3 scripts/audit_session.py --scope triage --output-dir "$REPORT_DIR"
# 可选，仅对用户明确选定项目的 Cargo target:
python3 scripts/audit_session.py --scope developer --project-root "$HOME/Developer/your-project" --output-dir "$REPORT_DIR"
```

`complete_within_policy` 仅代表获准技术目标覆盖完成；隐私排除不算错误。`home_total_measured=false` 是正常设计，不意味着全 Home 占用为零。默认报告不含完整路径、主机名、PID 或进程命令行。`--details` 仅在用户明确要求本机详细分析时启用。

## AI 与清理的分工
用户先请 AI 分析特定目标、风险及重建成本。`triage_home.py` 只产生安全状态和空间证据；即使标 `REVIEW` 也不代表建议删除。AI 可以针对明确选定的应用缓存编写 schema v3 清理计划（包含 `ai_analysis` 与 `conditions`），但仍需用户逐项批准。

```bash
python3 scripts/cleanup_plan.py --plan approved-plan.json   # dry-run；绝不删除
# 禁止在验收中自动运行 --apply。用户单独明确授权后才可考虑实际执行，仍需本机终端输入 DELETE。
```

所有真实个人数据、项目源码、数据库、账号信息、工作区根目录以及个人隐私目录均不会由此默认审计/自动清理。严禁自动停止用户进程、尝试提升 TCC/FDA 或对敏感目录执行探测。详见 `references/privacy-threat-model.md`。

## 验收
G0–G7：版本读取、真实设备连接、原版部署、哈希校验、普通用户隔离夹具测试、真实受限审计、AI 人工分析、隐私边界。G4 测试只在 Mac 上的临时 HOME 创建及清理测试文件，绝不对真实用户文件进行删除。保存测试 stdout/stderr、退出码、版本及原版脚本哈希。不能用 ad-hoc shell 审计冒充原版工具通过。
