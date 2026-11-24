# Evidence Nanopub

一个用于科研文献阅读的 Agent Skill。它把论文结论拆成可单独核验的断言，为每条断言保留原文位置、实验条件和来源，并检查比较对象与数值是否对应。适用于玻尔北化分站赛「阅读14｜Nanopublication」。

## 使用

让 Agent 加载 [SKILL.md](./SKILL.md)，提供论文材料及要回答的问题。例如：“表 2 中哪一组产率更高？请给出两组读数、适用条件和证据位置。” Agent 根据任务要求导出结构化结果，并标记证据不足或相互冲突之处。

两个校验脚本使用 Python 3.8+ 标准库，可以单独运行。

| 工具 | 校验内容 |
| --- | --- |
| [check_quotes.py](./check_quotes.py) | 检查逐字引文能否在指定页段或表注的转录文本中找到，允许空白差异。 |
| [check_table.py](./check_table.py) | 按原表的行名与含单位的列名，核对两个十进制读数和比较方向。 |

## 复现一次数值归属错误

下面是虚构的教学示例。在脚本所在目录保存两个 UTF-8 文件。原表 `table.csv` 为：

```csv
Group,Yield (%)
A,61
B,78
```

待核验的 `claim.json` 把两组数值写反了：

```json
{"metric":"Yield (%)","left":"B","right":"A","left_value":"61","right_value":"78","relation":"lt"}
```

运行 `python check_table.py table.csv claim.json`。输出中的 `observed` 给出原表读数，`issues` 指出 B 应为 78、A 应为 61，且 B 大于 A。将两个读数分别改为 `"78"`、`"61"`，关系改为 `"gt"`，再次运行，`issues` 应为空。

## 适用边界

表格核验要求组名和列名可唯一定位。遇到重复行名、带误差范围的读数或单位不匹配时，需回原表复核。引文匹配只能确认文字出现在指定位置；证据能否支持因果关系、脚注限定哪些组，以及差异是否具有统计显著性，仍需结合原文判断。
