# Dead Frontier 内购上线配置清单（App Store Connect + GitHub Secrets）

按顺序执行。标 ✅ 的代码侧工作已完成；其余需要你在 Apple / GitHub 网页端操作。
任何证书、私钥、API Key **只进入 GitHub Secrets，绝不写入仓库文件**。

---

## 一、App Store Connect（https://appstoreconnect.apple.com）

### 1. 协议与税务
- [ ] 以 Account Holder 身份登录 → **Business**（协议、税务和银行业务）
- [ ] 签署 **Paid Apps** 协议，完成税务表单和银行账户（否则无法创建内购商品）

### 2. App 记录
- [ ] 新建 App（或确认已存在），Bundle ID 必须与工程一致
      （当前工程占位 `com.nightfall.deadrun`，替换成真实值后同步三处：
      `export_presets.cfg` 的 `application/bundle_identifier`、
      `.github/workflows/build-ios-signed.yml` 的 `BUNDLE_ID`、描述文件）
- [ ] 记下 **Team ID**（10 位，Membership 页面），填入 workflow 的 `APPLE_TEAM_ID`

### 3. 内购商品（In-App Purchases → 管理）
全部 36 个商品（与 `scripts/iap_service.gd` 的 `PRODUCTS` 表一一对应），参考名称随意、
本地化至少 en-US + zh-Hans，价格档位自选
（游戏内显示 StoreKit 本地化价格，代码里无硬编码）。

**Consumable（金币，9 个）**

| 商品 ID | 档位内容 |
|---|---|
| com.deadfrontier.coins.300 | 300 金币 |
| com.deadfrontier.coins.1650 | 1650 金币（含 10% 赠送） |
| com.deadfrontier.coins.3500 | 3500 金币（含 17% 赠送） |
| com.deadfrontier.coins.7400 | 7400 金币（含 23% 赠送） |
| com.deadfrontier.coins.19500 | 19500 金币（含 30% 赠送） |
| com.deadfrontier.coins.41000 | 41000 金币（含 37% 赠送） |
| com.deadfrontier.coins.5000 | 5000 金币 |
| com.deadfrontier.coins.50000 | 50000 金币 |
| com.deadfrontier.coins.500000 | 500000 金币 |

**Consumable（券，6 个）**：com.deadfrontier.vouchers.1 / 5 / 10 / 25 / 50 / 100

**Consumable（罐头，6 个）**：com.deadfrontier.cans.10 / 30 / 60 / 150 / 300 / 600

**Consumable（限时礼包，4 个）**：com.deadfrontier.offer.supply / offer.arms /
offer.hoard / offer.cans.150

**Non-Consumable（一次性，9 个）**：
- com.deadfrontier.removeads（永久去广告）
- com.deadfrontier.bundle.starter、com.deadfrontier.bundle.supply、com.deadfrontier.bundle.legend
- com.deadfrontier.char.darius、com.deadfrontier.char.maya、com.deadfrontier.skin.maya.tactical
- com.deadfrontier.pet.0 ~ pet.3

> ⚠️ 注意：`iap_service.gd` 的 `PRODUCTS` 表必须与商品 ID 完全一致
> （已对齐，见 `scripts/iap_service.gd` 顶部注释）。漏建的商品会在商店里显示 "…" 且不可购买。

- [ ] 每个商品：状态准备提交（Ready to Submit）需通过审核所需的截图/描述

### 4. Sandbox 测试
- [ ] Users and Access → Sandbox Testers → 新建测试员（专用测试 Apple ID，勿用主账号）
- [ ] 设备上登录 Sandbox：设置 → App Store → Sandbox Account（iOS 17+ 路径）

---

## 二、签名材料（Apple Developer → GitHub Secrets）

### 1. 证书 + 描述文件
- [ ] developer.apple.com → Certificates → 新建 **Apple Distribution** 证书
      （CSR 可用钥匙串访问生成；无 Mac 可用在线 CSR 工具或先跑 CI 时报错信息辅助）
- [ ] Profiles → 新建 **App Store** 类型描述文件，绑定上面证书 + 目标 Bundle ID，
      下载 `.mobileprovision`
- [ ] 把证书导出为 `.p12`（钥匙串访问 → 导出，设密码）

### 2. App Store Connect API Key（用于上传 TestFlight）
- [ ] App Store Connect → Users and Access → Integrations → **App Store Connect API**
      → 生成密钥（角色 Admin 或 Developer），下载 `AuthKey_XXXXXX.p8`，记下
      **Key ID** 和 **Issuer ID**

### 3. 写入 GitHub Secrets
仓库 → Settings → Secrets and variables → Actions → New repository secret：

| Secret 名 | 内容 | 生成命令（Git Bash） |
|---|---|---|
| `BUILD_CERTIFICATE_BASE64` | .p12 的 base64 | `base64 -w0 证书.p12` |
| `P12_PASSWORD` | .p12 导出密码 | 纯文本 |
| `BUILD_PROVISION_PROFILE_BASE64` | .mobileprovision 的 base64 | `base64 -w0 profile.mobileprovision` |
| `KEYCHAIN_PASSWORD` | 任意强密码（CI 建临时钥匙串用） | 纯文本 |
| `ASC_KEY_ID` | API Key ID（如 A1B2C3D4E5） | 纯文本 |
| `ASC_ISSUER_ID` | Issuer ID（UUID） | 纯文本 |
| `ASC_AUTH_KEY` | .p8 的 base64 | `base64 -w0 AuthKey_XXXX.p8` |

- [ ] 同时把 workflow 顶部 env 的 `APPLE_TEAM_ID`、`BUNDLE_ID`、`PROFILE_NAME` 改为真实值

---

## 三、构建与测试

- [ ] Actions → **Build iOS (signed) and upload to TestFlight** → Run workflow
- [ ] 成功后 App Store Connect → TestFlight 出现构建，等待处理（几分钟到几十分钟）
- [ ] 设备安装 TestFlight 版，用 Sandbox 账号跑测试矩阵：
  - [ ] 购买金币包 → 金币到账、按钮防连点
  - [ ] 取消购买 → 无奖励、有取消提示
  - [ ] 断网购买 → 失败弹窗，重试可用
  - [ ] Ask to Buy（Sandbox 可模拟）→ pending 提示，批准后到账
  - [ ] 购买后立刻杀进程重进 → 交易补投（proceedUnfinishedTransactions）、**不重复发放**
  - [ ] removeads 购买 → 去广告生效；卸载重装 → 恢复购买找回
  - [ ] 退款（App Store Connect 可退 Sandbox 订单）→ revoke 处理
- [ ] 全部通过后，workflow 里取消注释 `push: branches: [main]` 触发器（可选）

---

## 四、提交审核前检查

- [ ] 商城内无硬编码价格（真机显示 StoreKit 价格）✅ 代码已实现
- [ ] 模拟购买在 release 模板中禁用 ✅（`iap_service.gd sim_allowed()`）
- [ ] App 隐私标签声明 "Purchases" 数据用途
- [ ] 去广告商品在审核截图/录屏中可演示
