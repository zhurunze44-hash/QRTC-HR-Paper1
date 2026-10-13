# Paper1 / QRTC-HR GitHub 交付包独立复审（2026-10-13）

## 审核范围和限制

本报告独立读取并交叉核对上传的 `VERIFY_REPORTS_FOR_CHAT.zip` 中的交付报告、复现审计、纳入/排除清单及 README 等共 25 个文件；该压缩包通过 ZIP 完整性测试。本轮**没有拿到**原始约 532 MiB 的 `PAPER1_COMPLETE_FOR_GITHUB.tar.gz` 或内部约 509 MiB 的 `.tar.zst`，所以无法自行对 1567 个源文件重算 SHA256、扫描二进制内容、核实源码实际可执行性或从 GitHub 重新下载。

### 本轮独立复算通过

- `INCLUSION_MANIFEST.tsv`：1567 行；1567 个不同 SHA256；1567 个不同发布路径；`bytes` 累加 **2,004,510,293** 字节；`.pth` 21 个，累计 **1,734,868,337** 字节。
- `EXCLUSION_MANIFEST.tsv`：24 行，24 个不同 SHA256；`bytes` 累加 **388,196,944** 字节。
- 纳入∩排除哈希仅有一个：`76babe51db04c38d37fdbff3d1e1520c3243f7d19c3128f9642a38a99243e4df`，为不同目录下的同内容 `FOR_GPT_A1_EXECUTION_GUARD_PATCH_RETURN.zip`（25,309 字节）。
- 唯一字节数对账：2,004,510,293 + 388,196,944 − 25,309 = **2,392,681,928**，与 inventory 一致。
- 唯一文件数对账：1567 + 24 − 1 = **1590**；重复哈希条目数 3556 − 1590 = **1966**。报告中 `dedup_entries=1965` 表示以发布分类排除之后的路径去重数量：1567 + 24 + 1965 = 3556。需在交付说明中写明这两个统计口径。
- 两份纳入清单 SHA256 一致，两份排除清单 SHA256 一致。
- `publish_relpath` 均按 `frozen_assets/<canonical_source_path>` 映射；未发现重复发布路径或明显 `../` 穿越路径。

### 不能由本轮独立证明的事项

- `.tar.zst` 实际存在、大小、SHA256 和 1567 个源文件的真实字节内容，只能看到先前报告所声称的本地验证。
- `.pth` 是否能被正式方法代码加载、是否与对应配置兼容，以及能否通过冻结评估获得论文指标。
- `scripts/download_assets.sh`、`scripts/verify_assets.py`、`evaluation/eval_and_predict.py` 的实际内容和可执行性（本次材料未附这些脚本）。
- `DEDUP_PUBLICATION_MAP.tsv` 是否确实存在且能恢复原始实验路径中所需的 1965 个重复路径。
- 旧 GitHub 中空文件/ LFS 是否修复以及新的 Code 和 Release 是否可以公开访问。

## 发布前必须处理的阻断项

1. **上游数据再分发权利未核实。** `07_DATA_RIGHTS_AND_EXCLUSIONS.md` 明确写明 PC_KEGG 和 LncTarD 派生图未独立清理许可。公开 Release（甚至向受限人员分发）前，需分别确认数据许可证、来源和允许的再分发方式。不允许再分发的原始或派生文件改为数据获取/再生成指引，而不是强行打包发布。
2. **拟发布内容过宽。** 纳入清单含 `JIIS_SUBMISSION_20261003/` 27 个文件（包括投稿 cover letter PDF、编译日志和稿件图像）、`PAPER1_CMPB_FINAL_NO_NEW_TRAINING_V1_20261002/` 30 个文件（包括投稿 cover letter、审稿人画像、response bank、stop-loss policy 等）以及 `jiis/QRTC_HR_JIIS_submission_package.zip`。这些是投稿/内部流程材料，不是审稿人运行 QRTC-HR 必要输入。建议在独立公开版中排除，原版保留离线存档。
3. **敏感扫描仍需关闭。** `SENSITIVE_SCAN_HITS.txt` 记录 42 个路径，其中与纳入清单的规范路径直接匹配 21 个；命中本身不证明有凭证，但提供的包没有内容级逐条清理证据。另外纳入了若干 `.zip`、`.tar.gz` 和历史 `.parts/` 归档，顶层排除有凭证脚本不能证明嵌套归档中绝无其副本。应递归检查归档中的敏感内容，必要时只公开经确认的解包文件。
4. **已有凭证暴露风险。** 排除清单和报告提到历史 restore/upload 脚本有硬编码 SSH 口令。若口令仍在用，需要离线更换；同时检查旧 Git 历史或曾发布的 Release 是否曾包含凭证。仅在新包中排除不能撤销旧暴露。
5. **GitHub 尚未发生任何发布和验证。** `10_FINAL_TERMINAL.json`：G1/G5/G6/G7/G8 均 HOLD，远端下载 0，GitHub 源码 commit null，终态 `HOLD__GITHUB_AUTH_REQUIRED`，且仓库身份未确定。旧空文件的问题仍未解决。
6. **科研可复现级别不能越界。** 已知完整正式 5-seed panel 缺失、`PC_WOBRG_MAY02_QRTC` checkpoint 缺失、10 月 5 日证据中 live replay 未运行。21 个 `.pth` 中还有名称为 `BAD_RERUN`、`NOT_MAY02` 的资产；不能把所有 checkpoint 统称为有效正式主结果权重。

## 其他需要整理的发布质量问题

- `07_final_delivery/02_SOURCE_TO_GITHUB_MANIFEST.tsv` 只有一条 `LOCAL_READY` 占位记录，不是完整的 GitHub Code/Release 路径映射，不能当成已完成的交付清单。应给每个公开文件提供真实路径/URL 或发布包定位。
- `07_final_delivery/04_RELEASE_ASSET_LIST.tsv` 将 `CHECKSUMS.sha256` 记为 110 字节，但提供的该文件实测 **107** 字节；修正元数据。
- 单独的 `paper1-...tar.zst.sha256` 文件引用服务器绝对路径 `<REDACTED_SERVER_PATH> `sha256sum -c`；提供的 `CHECKSUMS.sha256` 用文件名引用才适合公开，或改写为相对路径。
- README 仍有 `<PUBLISHED_REPO_URL>`、`<owner>/<name>` 占位符。上传后须替换真实 URL、tag 和 commit SHA 并验证脚本。
- 尚未检验源码完整性、固定环境、评估入口、参数文件和依赖下载是否可正常使用；本地哈希通过只证明归档一致性，不证明模型评估可以复现。
- 公共复现仓库优先选独立的 Paper1 项目仓库；不要因便利而把包含其他项目/其他成员内容的实验室仓库整体改为 Public。私人仓库的 Release 不允许未经授权的外部审稿人直接获取。

## 最终裁决

**LOCAL_INVENTORY_ACCOUNTING = PASS**（对上传的小报告包中的清单进行独立复算）。

**ORIGINAL_ARCHIVE_BYTES_INDEPENDENTLY_VERIFIED = NOT_TESTED**（原始 509/532 MiB 大包未上传）。

**PUBLIC_RELEASE_SECURITY_AND_DATA_RIGHTS = HOLD**（内部投稿材料、嵌套归档、数据再分发许可尚未清理）。

**GITHUB_PUBLICATION_AND_REMOTE_VERIFICATION = HOLD**（Code、Release、旧空文件和远端下载均未确认）。

**SCIENTIFIC_REPRODUCIBILITY = PARTIAL_DISCLOSED**（不可宣称 Fully reproducible）。

建议完整原包只用于**离线主档**。保持冻结科研资产本身不变，另按允许公开的文件列表生成 **public/reviewer 版**：源码 + 配置 + 必要的合法数据或官方数据获取流程 + 冻结主结果权重 + 评估脚本 + 结果与哈希证据 + 已知局限。重新计算新包 SHA256，保留旧原包不动。随后 GitHub Code 公开真实源文件、Draft Release 上传新冻结包、外部无登录下载并完整哈希核验，再正式发布。

## 复审补充：仓库版 README 的可用性

`README.md` 把本次发布会话下的 `PAPER1_GITHUB_PUBLICATION_20261013/07_final_delivery/` 当作参考报告位置，但发布范围说明明确说发布工作区本身不纳入冻结包。必须把审稿人需要的审计报告复制进公开版仓库的 `docs/`，并改写链接为相对于仓库或 GitHub Release 的真实路径。`INCLUSION_MANIFEST.tsv` 还包含服务器绝对路径 `original_path`；公开版可在保留原始内部清单的前提下，另外生成路径归一化的公开清单，不必暴露服务器账号和本地部署路径。
