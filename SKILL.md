---
name: evidence-nanopub
description: Extract independently testable scientific assertions from supplied papers, preserve comparison conditions, and verify quoted evidence against located passages for nanopublication tasks.
---

# 从论文到可核验断言

## 接收案例

读取 /input/case.json、随题 task.md、output_contract 和实际材料。先记录 case_id、待回答的问题、材料版本及输出契约。遵照案例指定的字段、类型和序列化格式。将中间材料写在 /app/work，尽早在 /app/output/result.json 保存符合契约的部分结果，再补足证据和最终状态。按案例要求保留来源、不确定性与更改记录。

## 从证据生成断言

1. 建立来源索引。为每份实际材料分配稳定的本地标识，记录文件名、题名、作者、年份、版本和材料中确实出现的 DOI 或其他标识符。缺字段记为未知。区分作者的观察与作者转述的其他论文。
2. 按页与段、表格行列或图号及面板划分证据。赋予位置键，例如 paper1:p4:table2:rowB；保存忠实转录的文字。表格记录表头、单位、行名、脚注各自的位置。正文提及图表时，读取实际图表。只有扫描图时检查可用 OCR 并核对原图，字迹无法确认就标出具体位置和缺失字段。
3. 每条断言写清主体、关系、对象或比较基线、方向、数值与单位、适用条件。限定词随断言保留。以“改变一个结果是否仍可能保留另一个结果”为拆分依据。不同终点分别记录；同一比较的两组数值保留在同一断言。
4. 为断言挑选最短的充分证据组合。逐项指出主体、关系、对象及条件各来自哪里。用删除检验检查每个证据片段：移走它仍能支持全部要素时，可将它移出证据集。分散在表头、单元格和方法段的证据分别引用。原文与译述分字段保存。
5. 复核语义。交换两组名称后，证据是否还能被误认为支持结论？删除人群、温度或观察时间后，范围是否被夸大？保留否定、误差和未经检验的差异。按证据区分观察、关联、干预比较、作者推断和未决关系。因果解释须有独立证据。当正文与表格冲突，输出两处定位与各自读数，标为冲突并说明可确认的部分。
6. 依实际任务生成标识稳定的断言记录，包含证据位置、来源标识、支持类型及置信依据。同一来源版本、条件、方向、对象均一致时才合并重复断言，并保留证据合集。若案例要求 RDF，按指定词表、命名图与序列化导出并用可用解析器回读。最终以原始 output_contract 为准。

## 核对原文定位

把源文件实际提取出的定位文本保存为 JSON 对象，键为位置、值为原文。独立从断言记录导出证据清单，列出断言 ID、位置和逐字引文。不要用生成的引文反向构造原文索引。用 Python 3.8+ 标准库运行：

```sh
python /skills/weekly-skill/check_quotes.py /app/work/passages.json /app/work/quotes.json
```

脚本只折叠空白，校验引文在指定位置能否找到；退出码 0 表示全部匹配，1 表示存在定位问题，2 表示输入异常。回原文修复或标记未决。成功匹配仍须执行第 5 步语义复核。无法读取材料时报告受影响的材料和可接手位置，区分原文未报告、证据冲突、工具失败。最后解析 result.json 并对照案例契约逐项核对。

## 最小调用示例（虚构教学材料）

对于原表含可比较的十进制读数，使用同目录的 `check_table.py table.csv claim.json`（用 Python 3 运行）。从原表独立导出 UTF-8 CSV，首列为组名，后续列沿用含单位的原始表头。另从待核验断言填写比较对象、两个读数和方向。例如原表：

```csv
Group,Yield (%)
A,61
B,78
```

若表注另写“Both yields were measured at 80 °C.”，在断言中保留温度并用引文脚本定位这条脚注。下列比较文件对应“B 的产率高于 A”：

```json
{"metric":"Yield (%)","left":"B","right":"A","left_value":"78","right_value":"61","relation":"gt"}
```

工具比较的是指定列的原始读数。每条比较运行一次。输出 observed 供回看，issues 列出数值或方向冲突。退出码 2 表示无法核验，例如同名行、非纯数值或缺少列。含不等号、误差范围、多层表头或脚注限定时，保留原样并回到原表复核；只在列、组和数值能无歧义转录时使用此检查。表注的适用范围和统计显著性由 Agent 结合上下文另行核定。

输入 passages.json：

```json
{"demo:p1:s2":"At 80 °C, yield was 61% with A and 78% with B."}
```

任务为比较 A 与 B。示意断言为“在 80 °C 下，B 的产率为 78%，高于 A 的 61%”，来源为 demo，位置为第 1 页第 2 句。此处提供直接读数，统计显著性未报告。将以下内容保存为 quotes.json，在脚本所在目录运行 `python check_quotes.py passages.json quotes.json`，示意输出为 `{"checked": 1, "issues": []}`。

```json
[{"claim_id":"c1","locator":"demo:p1:s2","quote":"At 80 °C, yield was 61% with A and 78% with B."}]
```
