# 农银匠心灵动14天 第9期 G · 净值看板

手机优先的单页看板，展示 `NYJXLD1409G` 最近 90 个净值日的走势与每万份收益。

数据由 GitHub Actions 定时从农银理财官网抓取，自动提交到 `docs/index.html`，通过 GitHub Pages 托管。

## 访问

启用 Pages 后：

```
https://liuliutv1.github.io/abc1409-dashboard/
```

任何设备、任何网络都能打开，不依赖任何本地电脑。

## 更新节奏

| 北京时间 | 说明 |
|---|---|
| 09:00 | 早间补抓（覆盖前一晚遗漏） |
| 20:00 / 21:00 / 22:00 / 23:00 | 披露时段每小时抓一次 |

也可在 Actions 页面手动触发 `workflow_dispatch`。

当天净值未披露时，页面顶部显示黄色 **待更新** 徽章，不会用旧数据冒充今天。

## 指标口径

- **单位净值**：农银理财官网披露值
- **每万份收益** = 相邻两个净值日的净值差 × 10000（元/万元）
- **近 N 天累计万收** = 窗口内每日万份收益之和

## 本地运行

```bash
python fetch_and_build.py
# 输出 docs/index.html
```

无第三方依赖，仅用标准库 `urllib`。

## 目录

```
fetch_and_build.py            抓取 + 生成单页
docs/index.html               生成产物（Pages 发布源）
.github/workflows/update.yml  定时任务
```

## 免责

数据仅搬运官网公开披露，不构成投资建议。净值型产品可能亏损，历史收益不代表未来表现。
