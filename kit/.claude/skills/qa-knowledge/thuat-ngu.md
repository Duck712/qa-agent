# Thuật ngữ kiểm thử Việt – Anh – Nhật (ISTQB / JSTQB)

> Dùng khi viết **Test Plan, báo cáo, Q&A, file gửi khách** — để gọi đúng tên mà người đọc đã quen. Không đổi
> cách test. Bảng chỉ nói "gọi là gì", cách làm vẫn theo `qa-testcase-design` và các skill khác.

## Luật dùng
1. **Mẫu / file của khách dùng chữ nào thì giữ đúng chữ đó** (vd mẫu ghi 試験 thì không đổi thành テスト, mẫu ghi
   ＮＧ数 thì không đổi thành 欠陥数). Bảng này chỉ dùng cho câu mình tự viết thêm.
2. Một khái niệm dùng **một** tên trong cả file. Lần đầu có thể ghi kèm tiếng Anh trong ngoặc nếu người đọc lẫn lộn.
3. Viết cho người không rành kỹ thuật thì ưu tiên lời thường; thuật ngữ chỉ dùng khi nó làm câu rõ hơn.
4. Không chắc chữ tiếng Nhật → tra JSTQB 用語集 (jstqb.jp) hoặc hỏi người dùng, không tự đặt chữ mới.

## 1. Quy trình và tài liệu

| Tiếng Việt (trong bộ này) | ISTQB (EN) | JSTQB (JA) |
|---|---|---|
| Kế hoạch test | Test plan | テスト計画書 |
| Phạm vi test | Test scope | テスト範囲 / テスト対象 |
| Căn cứ test (đặc tả, thiết kế…) | Test basis | テストベース |
| Phân tích test | Test analysis | テスト分析 |
| Thiết kế test | Test design | テスト設計 |
| Chạy test | Test execution | テスト実行 |
| Theo dõi và điều chỉnh | Test monitoring and control | テストモニタリングとテストコントロール |
| Kết thúc test | Test completion | テスト完了 |
| Báo cáo tiến độ | Test progress report | テスト進捗レポート |
| Báo cáo kết thúc | Test completion report | テスト完了レポート |
| Tiêu chí bắt đầu | Entry criteria | 開始基準 |
| Tiêu chí kết thúc | Exit criteria | 終了基準 |
| Điều kiện test / quan điểm test | Test condition | テスト条件（現場では「テスト観点」） |
| Test case | Test case | テストケース |
| Bước test | Test procedure | テスト手順 |
| Dữ liệu test | Test data | テストデータ |
| Kết quả mong đợi | Expected result | 期待結果 |
| Kết quả thực tế | Actual result | 実行結果 |
| Căn cứ đúng / sai (oracle) | Test oracle | テストオラクル |
| Môi trường test | Test environment | テスト環境 |
| Nhật ký chạy (RUNLOG) | Test log | テストログ |
| Ma trận truy vết | Traceability matrix | トレーサビリティマトリクス |
| Độ phủ | Coverage | カバレッジ |

## 2. Cấp độ và loại test

| Tiếng Việt | ISTQB (EN) | JSTQB (JA) | Ngành Nhật hay gọi |
|---|---|---|---|
| Test thành phần / đơn vị | Component testing | コンポーネントテスト | 単体テスト (UT) |
| Test tích hợp | Integration testing | 統合テスト | 結合テスト (IT) |
| Test hệ thống | System testing | システムテスト | 総合テスト (ST) |
| Test chấp nhận | Acceptance testing | 受け入れテスト | 受入テスト (UAT) |
| Test chức năng | Functional testing | 機能テスト | |
| Test phi chức năng | Non-functional testing | 非機能テスト | |
| Test lại bug đã sửa | Confirmation testing | 確認テスト | 再テスト |
| Test hồi quy | Regression testing | リグレッションテスト | 回帰テスト / デグレ確認 |
| Test tĩnh (review tài liệu) | Static testing | 静的テスト | レビュー |
| Test động (chạy phần mềm) | Dynamic testing | 動的テスト | |
| So sánh bản cũ với bản mới | (Back-to-back testing) | バックツーバックテスト | 現新比較 / 新旧比較 |

Tên cấp độ ở dự án Nhật (UT / IT / ST, PT…) **mỗi công ty định nghĩa một kiểu** → không suy từ bảng này; đọc Test Plan
hoặc hỏi khách (`ANALYSIS §5`).

## 3. Kỹ thuật thiết kế test

| Tiếng Việt | ISTQB (EN) | JSTQB (JA) |
|---|---|---|
| Phân vùng tương đương | Equivalence partitioning | 同値分割法 |
| Phân tích giá trị biên | Boundary value analysis | 境界値分析 |
| Bảng quyết định | Decision table testing | デシジョンテーブルテスト |
| Chuyển trạng thái | State transition testing | 状態遷移テスト |
| Theo use case / kịch bản | Use case testing | ユースケーステスト |
| Tổ hợp từng cặp | Pairwise testing | ペアワイズテスト |
| Cây phân loại | Classification tree method | クラシフィケーションツリー技法 |
| Phủ câu lệnh | Statement testing / coverage | ステートメントテスト / ステートメントカバレッジ |
| Phủ nhánh | Branch testing / coverage | ブランチテスト / ブランチカバレッジ |
| Đoán lỗi | Error guessing | エラー推測 |
| Test khám phá | Exploratory testing | 探索的テスト |
| Test khám phá theo phiên | Session-based testing | セッションベースドテスト |
| Test theo checklist | Checklist-based testing | チェックリストベースドテスト |
| Test theo rủi ro | Risk-based testing | リスクベースドテスト |
| Ca bình thường / bất thường | (Positive / negative testing) | 正常系 / 異常系（現場用語） |

## 4. Lỗi và rủi ro

| Tiếng Việt | ISTQB (EN) | JSTQB (JA) | Ngành Nhật hay gọi |
|---|---|---|---|
| Sai sót của người làm | Error / mistake | エラー / 誤り | |
| Khiếm khuyết trong sản phẩm | Defect / bug | 欠陥 | 不具合 / バグ |
| Hỏng khi chạy | Failure | 故障 | 障害 |
| Nguyên nhân gốc | Root cause | 根本原因 | |
| Báo cáo lỗi | Defect report | 欠陥レポート | 不具合票 / チケット起票 |
| Rủi ro sản phẩm | Product risk | プロダクトリスク | |
| Rủi ro dự án | Project risk | プロジェクトリスク | |

## 5. Đặc tính chất lượng (ISO/IEC 25010, tên thường gặp)

| Tiếng Việt | EN | JA |
|---|---|---|
| Phù hợp chức năng | Functional suitability | 機能適合性 |
| Hiệu năng | Performance efficiency | 性能効率性 |
| Tương thích | Compatibility | 互換性 |
| Dễ dùng | Usability | 使用性 |
| Tin cậy | Reliability | 信頼性 |
| Bảo mật | Security | セキュリティ |
| Dễ bảo trì | Maintainability | 保守性 |
| Dễ chuyển đổi môi trường | Portability | 移植性 |

Bản ISO/IEC 25010:2023 đổi một số tên (vd Usability → Interaction capability). Khách dùng bản nào thì theo bản đó.
