from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from topic_blueprints import TOPIC_BLUEPRINTS


OUTPUT_PATH = Path(__file__).with_name("discrete_math_questions.json")
KNOWLEDGE_OUTPUT_PATH = Path(__file__).with_name("discrete_math_knowledge_base.json")


def mc(topic, difficulty, question, options, answer, explanation, keywords):
    return {
        "type": "multiple_choice",
        "topic": topic,
        "difficulty": difficulty,
        "question": question,
        "options": options,
        "answer": answer,
        "explanation": explanation,
        "keywords": keywords,
    }


def sa(topic, difficulty, question, answer, explanation, keywords):
    return {
        "type": "short_answer",
        "topic": topic,
        "difficulty": difficulty,
        "question": question,
        "answer": answer,
        "explanation": explanation,
        "keywords": keywords,
    }


def essay(topic, difficulty, question, answer, explanation, keywords):
    return {
        "type": "essay",
        "topic": topic,
        "difficulty": difficulty,
        "question": question,
        "answer": answer,
        "explanation": explanation,
        "keywords": keywords,
    }


QUESTION_BANK = []

QUESTION_BANK.extend(
    [
        mc(
            "Tập hợp",
            "easy",
            "Tập hợp là gì?",
            [
                "Một bộ sưu tập các đối tượng được xác định rõ ràng và phân biệt được.",
                "Một phép toán luôn cho ra số nguyên.",
                "Một dãy số có thứ tự cố định.",
                "Một hàm số nhận đầu vào là số thực.",
            ],
            "Một bộ sưu tập các đối tượng được xác định rõ ràng và phân biệt được.",
            "Trong tập hợp, điều quan trọng là biết một đối tượng có thuộc tập hay không; thứ tự các phần tử không quan trọng.",
            ["tập hợp", "phần tử", "set", "định nghĩa tập hợp"],
        ),
        sa(
            "Tập hợp",
            "easy",
            "Thế nào là tập con của một tập hợp?",
            "A là tập con của B nếu mọi phần tử của A đều thuộc B, ký hiệu A ⊆ B.",
            "Để chứng minh A ⊆ B, ta cần chỉ ra rằng lấy bất kỳ x thuộc A thì x cũng thuộc B.",
            ["tập con", "subset", "bao hàm", "A thuộc B"],
        ),
        essay(
            "Tập hợp",
            "easy",
            "Phân biệt phép hợp, phép giao và phép hiệu của hai tập hợp.",
            "Phép hợp A ∪ B là tập gồm các phần tử thuộc A hoặc thuộc B. Phép giao A ∩ B là tập gồm các phần tử đồng thời thuộc cả A và B. Phép hiệu A \\ B là tập gồm các phần tử thuộc A nhưng không thuộc B.",
            "Ba phép toán này mô tả ba cách kết hợp thông tin khác nhau: gộp lại, lấy phần chung, và loại bỏ phần trùng với tập còn lại.",
            ["hợp", "giao", "hiệu", "union", "intersection", "difference"],
        ),
        mc(
            "Tập hợp",
            "easy",
            "Nếu tập A có 3 phần tử thì tập lũy thừa P(A) có bao nhiêu phần tử?",
            ["6", "8", "9", "16"],
            "8",
            "Một tập có n phần tử thì tập lũy thừa của nó có 2^n tập con. Với n = 3, ta được 2^3 = 8.",
            ["tập lũy thừa", "power set", "2 mũ n", "số tập con"],
        ),
        sa(
            "Tập hợp",
            "medium",
            "Tích Descartes A × B là gì?",
            "A × B là tập hợp tất cả các cặp có thứ tự (a, b) với a thuộc A và b thuộc B.",
            "Khác với tập hợp thông thường, trong cặp có thứ tự thì vị trí của từng phần tử là quan trọng.",
            ["tích descartes", "cặp có thứ tự", "cartesian product", "A x B"],
        ),
        essay(
            "Tập hợp",
            "medium",
            "Phát biểu và giải thích định luật De Morgan đối với tập hợp.",
            "Hai định luật De Morgan là: (A ∪ B)^c = A^c ∩ B^c và (A ∩ B)^c = A^c ∪ B^c. Chúng cho biết phần bù của phép hợp bằng giao các phần bù, còn phần bù của phép giao bằng hợp các phần bù.",
            "Ta có thể hiểu trực quan rằng một phần tử không thuộc A ∪ B khi và chỉ khi nó không thuộc A và cũng không thuộc B.",
            ["de morgan", "phần bù", "bổ sung", "luật tập hợp"],
        ),
        mc(
            "Tập hợp",
            "easy",
            "Số phần tử của tập rỗng là bao nhiêu?",
            ["0", "1", "2", "Vô hạn"],
            "0",
            "Tập rỗng không chứa phần tử nào nên lực lượng của nó bằng 0.",
            ["tập rỗng", "empty set", "số phần tử", "cardinality"],
        ),
        sa(
            "Tập hợp",
            "medium",
            "Một phân hoạch của tập hợp là gì?",
            "Phân hoạch của một tập hợp là cách chia tập đó thành các tập con khác rỗng, đôi một rời nhau và hợp của chúng bằng toàn bộ tập ban đầu.",
            "Mỗi phần tử của tập gốc phải thuộc đúng một khối trong phân hoạch.",
            ["phân hoạch", "partition", "chia tập hợp", "khối"],
        ),
        essay(
            "Tập hợp",
            "medium",
            "Hàm đặc trưng của một tập hợp dùng để làm gì?",
            "Hàm đặc trưng của tập A là hàm nhận giá trị 1 nếu phần tử thuộc A và nhận 0 nếu phần tử không thuộc A. Nó giúp biểu diễn tập hợp bằng ngôn ngữ hàm, rất tiện khi xử lý bằng logic hoặc máy tính.",
            "Nhờ hàm đặc trưng, nhiều phép toán trên tập hợp có thể chuyển thành các phép toán đại số hoặc logic trên giá trị 0 và 1.",
            ["hàm đặc trưng", "characteristic function", "0 1", "biểu diễn tập hợp"],
        ),
        mc(
            "Tập hợp",
            "easy",
            "Một tập có 5 phần tử thì có bao nhiêu tập con?",
            ["10", "25", "32", "64"],
            "32",
            "Một tập có n phần tử thì có 2^n tập con. Với n = 5, ta có 2^5 = 32.",
            ["số tập con", "2^n", "lực lượng", "count subsets"],
        ),
        mc(
            "Logic mệnh đề",
            "easy",
            "Mệnh đề là gì?",
            [
                "Một câu khẳng định có giá trị đúng hoặc sai xác định.",
                "Một câu hỏi chưa có lời giải.",
                "Một biểu thức luôn nhận giá trị số nguyên.",
                "Một dãy ký tự bất kỳ.",
            ],
            "Một câu khẳng định có giá trị đúng hoặc sai xác định.",
            "Trong logic mệnh đề, mệnh đề phải có chân trị rõ ràng, không được mơ hồ hay phụ thuộc cảm xúc.",
            ["mệnh đề", "proposition", "đúng sai", "logic"],
        ),
        sa(
            "Logic mệnh đề",
            "easy",
            "Mệnh đề kéo theo p → q có nghĩa là gì?",
            "p → q có nghĩa là nếu p đúng thì q phải đúng.",
            "Mệnh đề kéo theo chỉ sai trong trường hợp p đúng nhưng q sai.",
            ["kéo theo", "implication", "p suy ra q", "nếu thì"],
        ),
        essay(
            "Logic mệnh đề",
            "medium",
            "Phân biệt mệnh đề đảo, mệnh đề phản đảo và mệnh đề phản chứng của p → q.",
            "Mệnh đề đảo là q → p. Mệnh đề phản đảo là ¬p → ¬q. Mệnh đề phản chứng là ¬q → ¬p. Trong ba mệnh đề này, chỉ mệnh đề phản chứng luôn tương đương logic với mệnh đề gốc p → q.",
            "Việc phân biệt ba dạng này rất quan trọng vì người học thường nhầm mệnh đề đảo với mệnh đề tương đương.",
            ["mệnh đề đảo", "phản đảo", "phản chứng", "contrapositive"],
        ),
        mc(
            "Logic mệnh đề",
            "easy",
            "Mệnh đề p → q nhận giá trị sai khi nào?",
            [
                "Khi p sai và q sai.",
                "Khi p đúng và q sai.",
                "Khi p sai và q đúng.",
                "Khi p đúng và q đúng.",
            ],
            "Khi p đúng và q sai.",
            "Đây là trường hợp duy nhất làm vi phạm lời khẳng định 'nếu p thì q'.",
            ["bảng chân trị", "implication false", "p q", "logic kéo theo"],
        ),
        sa(
            "Logic mệnh đề",
            "easy",
            "Phủ định của mệnh đề p ∧ q là gì?",
            "Phủ định của p ∧ q là ¬p ∨ ¬q.",
            "Đây là một trong hai định luật De Morgan cơ bản của logic mệnh đề.",
            ["de morgan logic", "phủ định", "and or not", "p và q"],
        ),
        essay(
            "Logic mệnh đề",
            "medium",
            "Bảng chân trị là gì và dùng để kiểm tra hằng đúng như thế nào?",
            "Bảng chân trị liệt kê mọi khả năng đúng sai của các biến mệnh đề rồi tính giá trị của biểu thức logic tương ứng. Nếu biểu thức luôn đúng ở mọi dòng của bảng thì đó là hằng đúng; nếu luôn sai thì là mâu thuẫn.",
            "Bảng chân trị là công cụ trực quan và chắc chắn để kiểm tra tương đương logic hoặc tính đúng sai của biểu thức.",
            ["bảng chân trị", "hằng đúng", "tautology", "mâu thuẫn"],
        ),
        mc(
            "Logic mệnh đề",
            "easy",
            "Ký hiệu nào thường dùng cho phép tương đương logic?",
            ["∧", "∨", "↔", "¬"],
            "↔",
            "Ký hiệu ↔ biểu diễn 'khi và chỉ khi', tức hai mệnh đề có cùng giá trị chân trị.",
            ["tương đương", "biconditional", "iff", "ký hiệu logic"],
        ),
        sa(
            "Logic mệnh đề",
            "medium",
            "Phủ định của mệnh đề 'với mọi x, P(x)' là gì?",
            "Phủ định của 'với mọi x, P(x)' là 'tồn tại x sao cho không P(x)'.",
            "Đổi ∀ thành ∃ và phủ định mệnh đề bên trong là quy tắc cơ bản khi phủ định lượng từ.",
            ["lượng từ", "forall", "exists", "phủ định lượng từ"],
        ),
        essay(
            "Logic mệnh đề",
            "medium",
            "Phân biệt vị từ và mệnh đề.",
            "Mệnh đề là câu khẳng định đã có chân trị xác định. Vị từ là biểu thức chứa biến, chỉ trở thành mệnh đề khi ta gán giá trị cho biến hoặc đặt lượng từ thích hợp. Ví dụ 'x là số chẵn' là vị từ, còn '4 là số chẵn' là mệnh đề đúng.",
            "Vị từ giúp mô tả các tính chất tổng quát, còn mệnh đề biểu diễn một khẳng định hoàn chỉnh.",
            ["vị từ", "predicate", "mệnh đề", "logic vị từ"],
        ),
        mc(
            "Logic mệnh đề",
            "easy",
            "Biểu thức nào là một hằng đúng?",
            ["p ∧ ¬p", "p ∨ ¬p", "p → ¬p", "¬(p ∨ ¬p)"],
            "p ∨ ¬p",
            "Quy luật bài trung nói rằng với mọi mệnh đề p, hoặc p đúng hoặc phủ định của nó đúng.",
            ["hằng đúng", "tautology", "luật bài trung", "p hoặc không p"],
        ),
    ]
)

QUESTION_BANK.extend(
    [
        mc(
            "Cây",
            "easy",
            "Cây là gì trong lý thuyết đồ thị?",
            [
                "Đồ thị liên thông và không chứa chu trình.",
                "Đồ thị có đúng một đỉnh cô lập.",
                "Đồ thị mà mọi đỉnh đều có bậc 2.",
                "Đồ thị đầy đủ có hướng.",
            ],
            "Đồ thị liên thông và không chứa chu trình.",
            "Đây là định nghĩa cơ bản nhất của cây trong đồ thị vô hướng.",
            ["cây", "tree", "liên thông", "không chu trình"],
        ),
        sa(
            "Cây",
            "easy",
            "Lá của cây là gì?",
            "Lá là đỉnh có bậc 1 trong cây vô hướng, hoặc là đỉnh không có con trong cây có gốc.",
            "Lá thường biểu diễn các phần tử ở tầng cuối hoặc các trường hợp kết thúc của cấu trúc phân cấp.",
            ["lá", "leaf", "bậc 1", "cây"],
        ),
        essay(
            "Cây",
            "medium",
            "Nêu một vài tính chất cơ bản của cây.",
            "Nếu một đồ thị là cây có n đỉnh thì nó có đúng n - 1 cạnh. Giữa mọi cặp đỉnh của cây luôn có duy nhất một đường đi đơn. Thêm một cạnh bất kỳ vào cây sẽ tạo ra đúng một chu trình, còn bỏ một cạnh bất kỳ sẽ làm cây mất tính liên thông.",
            "Các tính chất này có thể dùng qua lại như những tiêu chuẩn nhận biết cây.",
            ["tính chất cây", "n-1 cạnh", "đường đi duy nhất", "tree properties"],
        ),
        mc(
            "Cây",
            "easy",
            "Một cây có n đỉnh thì có bao nhiêu cạnh?",
            ["n", "n - 1", "n + 1", "2n"],
            "n - 1",
            "Đây là một trong những định lý nền tảng nhất về cây.",
            ["n-1 cạnh", "tree edges", "cây", "đồ thị"],
        ),
        sa(
            "Cây",
            "medium",
            "Cây khung của một đồ thị liên thông là gì?",
            "Cây khung là một đồ thị con chứa tất cả các đỉnh của đồ thị gốc và là một cây.",
            "Cây khung giữ lại khả năng liên thông nhưng loại bỏ các chu trình thừa.",
            ["cây khung", "spanning tree", "đồ thị con", "liên thông"],
        ),
        essay(
            "Cây",
            "medium",
            "Cây có gốc là gì và các cách duyệt cây phổ biến gồm những gì?",
            "Cây có gốc là cây trong đó ta chọn một đỉnh đặc biệt làm gốc để xác định quan hệ cha - con. Các cách duyệt phổ biến gồm tiền tự, trung tự, hậu tự trong cây nhị phân và duyệt theo mức. Mỗi cách duyệt phục vụ những mục đích khác nhau như in biểu thức, xử lý thư mục hay tìm kiếm.",
            "Việc gắn gốc cho cây biến cấu trúc vô hướng thành cấu trúc phân cấp dễ thao tác trong khoa học máy tính.",
            ["cây có gốc", "duyệt cây", "preorder inorder postorder", "level order"],
        ),
        mc(
            "Cây",
            "medium",
            "Trong cây nhị phân đầy đủ, nếu có i nút trong thì số lá bằng bao nhiêu?",
            ["i", "i + 1", "2i", "2i + 1"],
            "i + 1",
            "Đây là hệ quả quen thuộc của quan hệ giữa số cạnh và số con trong cây nhị phân đầy đủ.",
            ["cây nhị phân đầy đủ", "số lá", "internal nodes", "i+1"],
        ),
        sa(
            "Cây",
            "easy",
            "Chiều cao của cây thường được hiểu là gì?",
            "Chiều cao của cây là độ dài đường đi dài nhất từ gốc đến một lá, thường tính theo số cạnh hoặc số mức tùy quy ước.",
            "Khi dùng tài liệu khác nhau, cần kiểm tra rõ người ta đếm theo cạnh hay theo đỉnh.",
            ["chiều cao cây", "height", "gốc đến lá", "tree depth"],
        ),
        essay(
            "Cây",
            "medium",
            "Nêu một số ứng dụng của cây trong khoa học máy tính.",
            "Cây được dùng để biểu diễn cấu trúc thư mục, cây phân tích cú pháp, cây tìm kiếm nhị phân, heap, trie và nhiều cấu trúc dữ liệu khác. Chúng phù hợp với các bài toán có cấu trúc phân cấp hoặc cần truy vấn, chèn, xóa hiệu quả.",
            "Tư duy về cây cũng xuất hiện trong đệ quy, biên dịch, trí tuệ nhân tạo và mạng máy tính.",
            ["ứng dụng của cây", "cấu trúc dữ liệu", "BST", "heap trie"],
        ),
        mc(
            "Cây",
            "easy",
            "Trong cây m-ary, mỗi nút trong có nhiều nhất bao nhiêu con?",
            ["m - 1", "m", "m + 1", "2m"],
            "m",
            "Đúng theo định nghĩa, cây m-ary cho phép mỗi nút trong có không quá m cây con.",
            ["m-ary tree", "số con", "cây đa phân", "định nghĩa"],
        ),
        mc(
            "Đại số Boole và thuật toán",
            "easy",
            "Biến Boole thường nhận những giá trị nào?",
            ["-1 và 1", "0 và 1", "0 và 2", "1 và 2"],
            "0 và 1",
            "Trong nhiều ngữ cảnh, 0 biểu diễn sai và 1 biểu diễn đúng.",
            ["biến boole", "0 1", "boolean variable", "logic số"],
        ),
        sa(
            "Đại số Boole và thuật toán",
            "easy",
            "Ba phép toán Boole cơ bản AND, OR, NOT có ý nghĩa gì?",
            "AND đúng khi cả hai đầu vào đều đúng, OR đúng khi có ít nhất một đầu vào đúng, còn NOT đảo giá trị đúng sai.",
            "Ba phép toán này là nền tảng của cả logic mệnh đề lẫn mạch số.",
            ["and or not", "phép toán boole", "logic cơ bản", "cổng logic"],
        ),
        essay(
            "Đại số Boole và thuật toán",
            "medium",
            "Giải thích vì sao biểu thức x + xy = x trong đại số Boole.",
            "Đây là luật hấp thụ. Nếu x = 0 thì cả hai vế đều bằng 0. Nếu x = 1 thì vế trái là 1 + y = 1, nên vẫn bằng 1. Vì vậy trong cả hai trường hợp, x + xy luôn bằng x.",
            "Luật hấp thụ cho phép rút gọn biểu thức logic trước khi thiết kế mạch hoặc tối ưu điều kiện truy vấn.",
            ["luật hấp thụ", "x + xy = x", "boolean algebra", "rút gọn"],
        ),
        mc(
            "Đại số Boole và thuật toán",
            "easy",
            "Đẳng thức nào đúng trong đại số Boole?",
            ["x + 0 = x", "x + 0 = 0", "x + 0 = 1", "x + 0 = x'"],
            "x + 0 = x",
            "0 là phần tử đơn vị của phép OR trong đại số Boole.",
            ["x cộng 0", "đại số boole", "phần tử đơn vị", "or"],
        ),
        sa(
            "Đại số Boole và thuật toán",
            "medium",
            "Bản đồ Karnaugh dùng để làm gì?",
            "Bản đồ Karnaugh dùng để rút gọn biểu thức Boole bằng cách nhóm các ô có giá trị 1 hoặc 0 theo các mẫu lân cận.",
            "Đây là công cụ trực quan giúp tối ưu số cổng logic trong mạch số cỡ nhỏ.",
            ["karnaugh", "rút gọn boole", "mạch logic", "K-map"],
        ),
        essay(
            "Đại số Boole và thuật toán",
            "medium",
            "Vì sao đại số Boole quan trọng trong thiết kế mạch số và xử lý điều kiện tìm kiếm?",
            "Đại số Boole cho phép biểu diễn các điều kiện đúng sai dưới dạng công thức có thể rút gọn và hiện thực bằng cổng logic. Trong mạch số, điều này giúp giảm số linh kiện và tăng hiệu quả. Trong truy vấn hoặc lập trình, các điều kiện AND, OR, NOT được tối ưu tương tự để đơn giản hóa xử lý logic.",
            "Đây là cầu nối rất rõ giữa toán rời rạc và khoa học máy tính thực hành.",
            ["đại số boole", "mạch số", "điều kiện logic", "ứng dụng boole"],
        ),
        mc(
            "Đại số Boole và thuật toán",
            "easy",
            "Ký hiệu Big O mô tả điều gì trong phân tích thuật toán?",
            [
                "Cận trên tiệm cận của tốc độ tăng thời gian hoặc bộ nhớ.",
                "Giá trị chính xác của thời gian chạy trên mọi máy.",
                "Số dòng lệnh trong chương trình.",
                "Số vòng lặp lớn nhất trong mã nguồn.",
            ],
            "Cận trên tiệm cận của tốc độ tăng thời gian hoặc bộ nhớ.",
            "Big O giúp mô tả xu hướng tăng trưởng khi kích thước đầu vào lớn, bỏ qua hằng số và hệ số bậc thấp.",
            ["big o", "độ phức tạp", "phân tích thuật toán", "asymptotic"],
        ),
        sa(
            "Đại số Boole và thuật toán",
            "easy",
            "BFS là gì?",
            "BFS là thuật toán duyệt đồ thị theo chiều rộng, thăm các đỉnh theo từng lớp khoảng cách từ đỉnh xuất phát.",
            "BFS thường dùng hàng đợi và rất hữu ích để tìm đường đi ngắn nhất trên đồ thị không trọng số.",
            ["bfs", "duyệt theo chiều rộng", "graph traversal", "queue"],
        ),
        essay(
            "Đại số Boole và thuật toán",
            "medium",
            "So sánh BFS và DFS trong duyệt đồ thị.",
            "BFS duyệt đồ thị theo từng lớp nên thích hợp để tìm khoảng cách ngắn nhất trên đồ thị không trọng số. DFS đi sâu theo một nhánh trước rồi quay lui, phù hợp cho việc kiểm tra liên thông, phát hiện chu trình hay sinh cấu trúc cây DFS. BFS thường dùng hàng đợi, còn DFS thường dùng ngăn xếp hoặc đệ quy.",
            "Hai chiến lược này là nền tảng cho nhiều thuật toán đồ thị nâng cao.",
            ["bfs và dfs", "duyệt đồ thị", "queue stack", "so sánh"],
        ),
        mc(
            "Đại số Boole và thuật toán",
            "easy",
            "Độ phức tạp thời gian của tìm kiếm nhị phân là gì?",
            ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
            "O(log n)",
            "Mỗi bước của tìm kiếm nhị phân loại bỏ một nửa không gian tìm kiếm nên số bước tăng theo logarit của n.",
            ["tìm kiếm nhị phân", "binary search", "log n", "độ phức tạp"],
        ),
    ]
)

QUESTION_BANK.extend(
    [
        mc(
            "Hệ thức truy hồi",
            "easy",
            "Hệ thức truy hồi là gì?",
            [
                "Một công thức biểu diễn số hạng hiện tại theo các số hạng trước đó.",
                "Một công thức luôn viết dưới dạng tích phân.",
                "Một bảng chân trị của mệnh đề logic.",
                "Một cách liệt kê phần tử của tập hợp.",
            ],
            "Một công thức biểu diễn số hạng hiện tại theo các số hạng trước đó.",
            "Hệ thức truy hồi mô tả một dãy bằng cách nêu mối liên hệ giữa các phần tử liên tiếp hoặc gần nhau.",
            ["truy hồi", "recurrence relation", "dãy", "đệ quy"],
        ),
        sa(
            "Hệ thức truy hồi",
            "easy",
            "Dạng truy hồi của một cấp số cộng là gì?",
            "Nếu d là công sai thì a_n = a_(n-1) + d với n ≥ 2.",
            "Muốn xác định hoàn toàn dãy còn cần một điều kiện đầu, chẳng hạn a_1.",
            ["cấp số cộng", "arithmetic sequence", "truy hồi", "a_n"],
        ),
        essay(
            "Hệ thức truy hồi",
            "medium",
            "Mô tả hệ Fibonacci bằng hệ thức truy hồi và giải thích ý nghĩa của nó.",
            "Dãy Fibonacci thường được cho bởi F_0 = 0, F_1 = 1 và F_n = F_(n-1) + F_(n-2) với n ≥ 2. Mỗi số hạng bằng tổng hai số hạng trước, nên dãy này là ví dụ kinh điển của truy hồi bậc hai.",
            "Fibonacci xuất hiện trong nhiều mô hình đếm và cũng là ví dụ mẫu khi học cách giải truy hồi tuyến tính.",
            ["fibonacci", "truy hồi bậc hai", "F_n", "dãy số"],
        ),
        mc(
            "Hệ thức truy hồi",
            "easy",
            "Với F_0 = 0, F_1 = 1 và F_n = F_(n-1) + F_(n-2), giá trị của F_5 là bao nhiêu?",
            ["3", "5", "8", "13"],
            "5",
            "Ta có F_2 = 1, F_3 = 2, F_4 = 3 và F_5 = 5.",
            ["fibonacci", "tính F5", "dãy truy hồi", "example"],
        ),
        sa(
            "Hệ thức truy hồi",
            "medium",
            "Hệ thức truy hồi tuyến tính thuần nhất là gì?",
            "Đó là hệ thức trong đó mỗi số hạng được biểu diễn như tổ hợp tuyến tính của các số hạng trước và không có hạng tự do ở vế phải.",
            "Ví dụ: a_n = 3a_(n-1) - 2a_(n-2) là truy hồi tuyến tính thuần nhất bậc hai.",
            ["tuyến tính thuần nhất", "linear homogeneous recurrence", "bậc hai", "truy hồi"],
        ),
        essay(
            "Hệ thức truy hồi",
            "medium",
            "Phương pháp phương trình đặc trưng dùng để giải truy hồi tuyến tính như thế nào?",
            "Với truy hồi tuyến tính thuần nhất có hệ số hằng, ta giả sử nghiệm có dạng r^n rồi thay vào hệ thức để thu được phương trình đặc trưng theo r. Giải phương trình này cho các nghiệm r, sau đó ghép lại thành công thức tổng quát và dùng điều kiện đầu để tìm hằng số cụ thể.",
            "Đây là phương pháp chủ đạo khi giải các truy hồi như Fibonacci, Lucas hoặc các dãy tuyến tính bậc hai, bậc ba.",
            ["phương trình đặc trưng", "characteristic equation", "giải truy hồi", "r^n"],
        ),
        mc(
            "Hệ thức truy hồi",
            "easy",
            "Một cấp số nhân với công bội r có thể viết dưới dạng truy hồi nào?",
            ["g_n = g_(n-1) + r", "g_n = r * g_(n-1)", "g_n = g_(n-1) - r", "g_n = r + n"],
            "g_n = r * g_(n-1)",
            "Mỗi số hạng của cấp số nhân bằng công bội nhân với số hạng ngay trước nó.",
            ["cấp số nhân", "geometric sequence", "g_n", "truy hồi"],
        ),
        sa(
            "Hệ thức truy hồi",
            "easy",
            "Điều kiện đầu trong bài toán truy hồi dùng để làm gì?",
            "Điều kiện đầu cung cấp các giá trị ban đầu để xác định duy nhất dãy thỏa hệ thức truy hồi.",
            "Không có điều kiện đầu thì thường sẽ có vô số dãy cùng thỏa một hệ thức truy hồi.",
            ["điều kiện đầu", "initial conditions", "xác định dãy", "truy hồi"],
        ),
        essay(
            "Hệ thức truy hồi",
            "medium",
            "So sánh công thức tường minh và công thức truy hồi.",
            "Công thức tường minh cho phép tính trực tiếp số hạng thứ n từ n mà không cần biết các số hạng trước. Công thức truy hồi mô tả cách tạo số hạng mới từ các số hạng cũ. Truy hồi thường dễ xây dựng từ bài toán gốc, còn công thức tường minh thuận tiện hơn khi cần tính số hạng xa hoặc phân tích tốc độ tăng trưởng.",
            "Trong thực hành, ta thường thiết lập truy hồi trước rồi mới tìm công thức tường minh nếu có thể.",
            ["công thức tường minh", "closed form", "truy hồi", "so sánh"],
        ),
        mc(
            "Hệ thức truy hồi",
            "medium",
            "Truy hồi x_n = 4x_(n-1) - x_(n-3) có bậc bao nhiêu?",
            ["1", "2", "3", "4"],
            "3",
            "Bậc của truy hồi được xác định bởi độ trễ lớn nhất xuất hiện, ở đây là n - 3.",
            ["bậc truy hồi", "order", "x_n", "n-3"],
        ),
        mc(
            "Lý thuyết đồ thị",
            "easy",
            "Đồ thị vô hướng là gì?",
            [
                "Một cấu trúc gồm tập đỉnh và tập cạnh nối các cặp đỉnh không có hướng.",
                "Một ma trận chỉ chứa số 0.",
                "Một cây có gốc duy nhất.",
                "Một tập con của mặt phẳng Euclid.",
            ],
            "Một cấu trúc gồm tập đỉnh và tập cạnh nối các cặp đỉnh không có hướng.",
            "Trong đồ thị vô hướng, cạnh {u, v} và {v, u} là cùng một cạnh.",
            ["đồ thị vô hướng", "graph", "đỉnh cạnh", "undirected"],
        ),
        sa(
            "Lý thuyết đồ thị",
            "easy",
            "Bậc của một đỉnh trong đồ thị vô hướng là gì?",
            "Bậc của đỉnh là số cạnh kề với đỉnh đó; nếu có khuyên thì mỗi khuyên được tính hai lần.",
            "Khái niệm bậc đỉnh rất quan trọng trong các định lý như bắt tay hay điều kiện Euler.",
            ["bậc đỉnh", "degree", "cạnh kề", "vertex"],
        ),
        essay(
            "Lý thuyết đồ thị",
            "easy",
            "Phân biệt đường đi, chu trình và đồ thị liên thông.",
            "Đường đi là dãy các đỉnh liên tiếp nhau qua các cạnh. Chu trình là đường đi đóng, tức bắt đầu và kết thúc tại cùng một đỉnh mà không lặp cạnh hoặc lặp đỉnh theo quy ước xét. Đồ thị liên thông là đồ thị trong đó mọi cặp đỉnh đều có đường đi nối với nhau.",
            "Ba khái niệm này là nền tảng để mô tả cấu trúc và khả năng di chuyển bên trong đồ thị.",
            ["đường đi", "chu trình", "liên thông", "path cycle connected"],
        ),
        mc(
            "Lý thuyết đồ thị",
            "easy",
            "Định lý bắt tay phát biểu điều gì?",
            [
                "Tổng bậc các đỉnh bằng số đỉnh.",
                "Tổng bậc các đỉnh bằng 2 lần số cạnh.",
                "Số đỉnh luôn lớn hơn số cạnh.",
                "Mọi đồ thị đều có chu trình.",
            ],
            "Tổng bậc các đỉnh bằng 2 lần số cạnh.",
            "Mỗi cạnh góp đúng 2 vào tổng bậc vì nó chạm vào hai đầu mút.",
            ["định lý bắt tay", "handshaking lemma", "2E", "tổng bậc"],
        ),
        sa(
            "Lý thuyết đồ thị",
            "easy",
            "Đồ thị đơn là gì?",
            "Đồ thị đơn là đồ thị không có khuyên và không có cạnh song song giữa cùng một cặp đỉnh.",
            "Đồ thị đơn là loại đồ thị thường gặp nhất trong các bài toán nhập môn.",
            ["đồ thị đơn", "simple graph", "khuyên", "cạnh song song"],
        ),
        essay(
            "Lý thuyết đồ thị",
            "medium",
            "Khi nào một đồ thị liên thông có chu trình Euler hoặc đường đi Euler?",
            "Một đồ thị liên thông có chu trình Euler khi mọi đỉnh đều có bậc chẵn. Nó có đường đi Euler nhưng không có chu trình Euler khi có đúng hai đỉnh bậc lẻ; khi đó đường đi bắt đầu ở một đỉnh lẻ và kết thúc ở đỉnh lẻ còn lại.",
            "Điều kiện Euler chỉ liên quan đến bậc đỉnh và tính liên thông, nên rất đẹp và dễ kiểm tra.",
            ["euler", "đường đi euler", "chu trình euler", "bậc lẻ chẵn"],
        ),
        mc(
            "Lý thuyết đồ thị",
            "medium",
            "Đồ thị đầy đủ K_n có bao nhiêu cạnh?",
            ["n", "n^2", "n(n-1)/2", "2n"],
            "n(n-1)/2",
            "Mỗi cạnh được xác định bởi một cặp đỉnh phân biệt nên số cạnh là số cách chọn 2 đỉnh từ n đỉnh.",
            ["đồ thị đầy đủ", "complete graph", "Kn", "số cạnh"],
        ),
        sa(
            "Lý thuyết đồ thị",
            "medium",
            "Đồ thị hai phía là gì?",
            "Đồ thị hai phía là đồ thị có thể chia tập đỉnh thành hai phần sao cho mọi cạnh đều nối một đỉnh ở phần này với một đỉnh ở phần kia.",
            "Một tính chất quan trọng là đồ thị hai phía không chứa chu trình lẻ.",
            ["đồ thị hai phía", "bipartite", "hai tập đỉnh", "chu trình lẻ"],
        ),
        essay(
            "Lý thuyết đồ thị",
            "medium",
            "Phân biệt chu trình Hamilton và chu trình Euler.",
            "Chu trình Hamilton đi qua mỗi đỉnh đúng một lần rồi quay về điểm xuất phát. Chu trình Euler đi qua mỗi cạnh đúng một lần rồi quay về điểm xuất phát. Một khái niệm tập trung vào đỉnh, khái niệm còn lại tập trung vào cạnh.",
            "Đây là hai bài toán khác nhau về bản chất: điều kiện Euler có mô tả đẹp, còn Hamilton khó hơn nhiều và không có tiêu chuẩn đơn giản tương tự.",
            ["hamilton", "euler", "chu trình", "đỉnh và cạnh"],
        ),
        mc(
            "Lý thuyết đồ thị",
            "easy",
            "Trong ma trận kề của đồ thị đơn vô hướng, phần tử A[i][j] bằng 1 khi nào?",
            [
                "Khi i = j.",
                "Khi có cạnh nối đỉnh i và đỉnh j.",
                "Khi bậc của i lớn hơn bậc của j.",
                "Khi đồ thị liên thông.",
            ],
            "Khi có cạnh nối đỉnh i và đỉnh j.",
            "Ma trận kề là cách biểu diễn đồ thị rất phù hợp cho máy tính khi cần kiểm tra nhanh xem hai đỉnh có nối với nhau hay không.",
            ["ma trận kề", "adjacency matrix", "Aij", "đồ thị"],
        ),
    ]
)

QUESTION_BANK.extend(
    [
        mc(
            "Hàm",
            "easy",
            "Hàm f: A → B được gọi là đơn ánh khi nào?",
            [
                "Mọi phần tử của B đều có đúng một phần tử của A ánh xạ tới.",
                "Hai phần tử khác nhau của A luôn có ảnh khác nhau trong B.",
                "Mọi phần tử của A có ít nhất hai ảnh trong B.",
                "Tập A và B phải có cùng số phần tử.",
            ],
            "Hai phần tử khác nhau của A luôn có ảnh khác nhau trong B.",
            "Đơn ánh nghĩa là hàm không gộp hai đầu vào khác nhau vào cùng một đầu ra.",
            ["đơn ánh", "injective", "one to one", "hàm"],
        ),
        sa(
            "Hàm",
            "easy",
            "Hàm toàn ánh là gì?",
            "Hàm toàn ánh là hàm mà mọi phần tử của tập đích đều là ảnh của ít nhất một phần tử trong tập nguồn.",
            "Toàn ánh đảm bảo không có phần tử nào của codomain bị bỏ trống.",
            ["toàn ánh", "surjective", "onto function", "tập đích"],
        ),
        essay(
            "Hàm",
            "medium",
            "Giải thích khái niệm song ánh và mối liên hệ với hàm ngược.",
            "Hàm song ánh là hàm vừa đơn ánh vừa toàn ánh. Khi đó mỗi phần tử của tập đích tương ứng đúng một phần tử của tập nguồn, nên ta có thể định nghĩa hàm ngược f^(-1) từ tập đích về tập nguồn. Ngược lại, một hàm có hàm ngược khi và chỉ khi nó là song ánh.",
            "Song ánh là công cụ trung tâm trong bài toán đếm vì nó cho phép thiết lập tương ứng một-một giữa hai tập.",
            ["song ánh", "bijection", "hàm ngược", "one to one correspondence"],
        ),
        mc(
            "Hàm",
            "medium",
            "Nếu A và B là hai tập hữu hạn có cùng số phần tử, một hàm f: A → B là đơn ánh thì điều gì đúng?",
            [
                "f cũng là toàn ánh.",
                "f không thể là toàn ánh.",
                "f không thể có hàm ngược.",
                "Không suy ra được điều gì thêm.",
            ],
            "f cũng là toàn ánh.",
            "Với hai tập hữu hạn có cùng lực lượng, đơn ánh và toàn ánh là tương đương nhau.",
            ["tập hữu hạn", "đơn ánh toàn ánh", "same size", "hàm hữu hạn"],
        ),
        sa(
            "Hàm",
            "easy",
            "Phân biệt miền xác định, miền giá trị và tập đích của hàm.",
            "Miền xác định là tập các đầu vào của hàm. Tập đích là tập mà hàm khai báo đi tới. Miền giá trị là tập các giá trị thực sự xuất hiện làm ảnh của các phần tử trong miền xác định.",
            "Miền giá trị luôn là tập con của tập đích, và hai khái niệm này không nên bị nhầm lẫn.",
            ["miền xác định", "tập đích", "miền giá trị", "domain codomain range"],
        ),
        essay(
            "Hàm",
            "medium",
            "Có bao nhiêu hàm từ tập A có 3 phần tử sang tập B có 2 phần tử? Giải thích.",
            "Có 2^3 = 8 hàm. Lý do là mỗi phần tử của A có 2 cách chọn ảnh trong B, và ba lựa chọn này độc lập với nhau nên theo quy tắc nhân ta có 2 × 2 × 2 = 8.",
            "Đây là công thức tổng quát: số hàm từ tập m phần tử sang tập n phần tử là n^m.",
            ["đếm số hàm", "n^m", "quy tắc nhân", "hàm từ A sang B"],
        ),
        mc(
            "Hàm",
            "easy",
            "Công thức đúng cho hợp thành của hai hàm f và g là gì?",
            ["(g ∘ f)(x) = f(g(x))", "(g ∘ f)(x) = g(f(x))", "(g ∘ f)(x) = g(x) + f(x)", "(g ∘ f)(x) = x"],
            "(g ∘ f)(x) = g(f(x))",
            "Ta áp dụng f trước rồi mới áp dụng g lên kết quả của f.",
            ["hợp thành hàm", "composition", "g of f", "g(f(x))"],
        ),
        sa(
            "Hàm",
            "medium",
            "Ảnh ngược của một tập con Y trong tập đích qua hàm f là gì?",
            "Ảnh ngược của Y là tập gồm mọi phần tử x trong miền xác định sao cho f(x) thuộc Y.",
            "Ảnh ngược giúp kéo một điều kiện ở tập đích về tập nguồn.",
            ["ảnh ngược", "inverse image", "preimage", "f inverse"],
        ),
        essay(
            "Hàm",
            "medium",
            "Vì sao song ánh quan trọng trong các bài toán đếm?",
            "Khi thiết lập được một song ánh giữa hai tập, ta biết hai tập có cùng số phần tử mà không cần đếm trực tiếp từng phần tử. Nhờ đó, nhiều bài toán tổ hợp có thể được giải bằng cách chuyển sang một tập khác dễ mô tả hoặc dễ đếm hơn.",
            "Đếm bằng song ánh là một tư duy rất mạnh vì nó thay phép đếm trực tiếp bằng lập luận cấu trúc.",
            ["song ánh trong đếm", "bijection counting", "đếm tổ hợp", "tương ứng một một"],
        ),
        mc(
            "Hàm",
            "medium",
            "Có bao nhiêu song ánh từ một tập n phần tử vào chính nó?",
            ["n", "2^n", "n!", "n^2"],
            "n!",
            "Một song ánh từ tập vào chính nó chính là một hoán vị của tập đó, nên có n! cách.",
            ["song ánh", "hoán vị", "bijection count", "n giai thừa"],
        ),
        mc(
            "Tổ hợp",
            "easy",
            "Theo quy tắc nhân, nếu có 3 cách chọn áo và 2 cách chọn quần thì có bao nhiêu bộ trang phục?",
            ["5", "6", "8", "9"],
            "6",
            "Hai quyết định độc lập nên số cách là 3 × 2 = 6.",
            ["quy tắc nhân", "multiplication principle", "đếm", "tổ hợp cơ bản"],
        ),
        sa(
            "Tổ hợp",
            "easy",
            "Hoán vị của n phần tử là gì?",
            "Hoán vị của n phần tử là một cách sắp xếp toàn bộ n phần tử đó theo một thứ tự nào đó.",
            "Số hoán vị của n phần tử phân biệt là n!.",
            ["hoán vị", "permutation", "sắp xếp", "n giai thừa"],
        ),
        essay(
            "Tổ hợp",
            "easy",
            "Phân biệt hoán vị và tổ hợp.",
            "Hoán vị dùng khi thứ tự các phần tử được chọn là quan trọng; tổ hợp dùng khi thứ tự không quan trọng. Ví dụ chọn ban cán sự có chức danh là bài toán hoán vị hoặc chỉnh hợp, còn chọn một nhóm học tập không phân vai là bài toán tổ hợp.",
            "Việc xác định 'thứ tự có quan trọng không' là bước mấu chốt khi làm các bài toán đếm.",
            ["hoán vị và tổ hợp", "thứ tự", "permutation vs combination", "đếm chọn"],
        ),
        mc(
            "Tổ hợp",
            "easy",
            "Giá trị của C(5, 2) bằng bao nhiêu?",
            ["5", "8", "10", "20"],
            "10",
            "C(5, 2) = 5! / (2!3!) = 10.",
            ["tổ hợp chập 2", "n choose k", "C52", "combination"],
        ),
        sa(
            "Tổ hợp",
            "medium",
            "Vì sao C(n, k) = C(n, n-k)?",
            "Vì chọn k phần tử để lấy cũng tương đương với chọn n-k phần tử để bỏ lại.",
            "Đẳng thức này được gọi là tính đối xứng của hệ số nhị thức.",
            ["đối xứng tổ hợp", "Cnk", "binomial coefficient", "chọn và bỏ"],
        ),
        essay(
            "Tổ hợp",
            "medium",
            "Nguyên lý Dirichlet hay nguyên lý chim bồ câu phát biểu như thế nào?",
            "Nếu phân phối nhiều hơn n đối tượng vào n hộp thì phải có ít nhất một hộp chứa từ hai đối tượng trở lên. Đây là một nguyên lý đơn giản nhưng rất mạnh trong chứng minh tồn tại.",
            "Ví dụ, trong một lớp có 13 người thì chắc chắn có ít nhất hai người sinh cùng tháng vì chỉ có 12 tháng.",
            ["nguyên lý dirichlet", "chim bồ câu", "pigeonhole principle", "chứng minh tồn tại"],
        ),
        mc(
            "Tổ hợp",
            "medium",
            "Có bao nhiêu cách sắp xếp các chữ cái của từ BANANA?",
            ["30", "60", "120", "720"],
            "60",
            "Từ BANANA có 6 chữ cái, trong đó A lặp 3 lần và N lặp 2 lần nên số hoán vị phân biệt là 6! / (3!2!) = 60.",
            ["hoán vị lặp", "BANANA", "sắp xếp chữ cái", "permutation with repetition"],
        ),
        sa(
            "Tổ hợp",
            "medium",
            "Công thức bao hàm - loại trừ cho hai tập A và B là gì?",
            "|A ∪ B| = |A| + |B| - |A ∩ B|.",
            "Khi cộng |A| và |B|, các phần tử thuộc cả hai tập bị đếm hai lần nên cần trừ đi một lần.",
            ["bao hàm loại trừ", "inclusion exclusion", "hai tập", "A union B"],
        ),
        essay(
            "Tổ hợp",
            "medium",
            "Giải thích công thức tổ hợp C(n, k) = n! / (k!(n-k)!).",
            "Ta có thể xem việc chọn k phần tử từ n phần tử là trước hết sắp xếp k phần tử được chọn theo thứ tự, tức có n(n-1)...(n-k+1) cách, rồi chia cho k! vì mỗi nhóm k phần tử bị đếm lặp qua mọi hoán vị của chính nó. Kết quả thu được là C(n, k) = n! / (k!(n-k)!).",
            "Lập luận này cho thấy công thức tổ hợp xuất phát tự nhiên từ việc loại bỏ ảnh hưởng của thứ tự.",
            ["công thức tổ hợp", "Cnk", "n giai thừa", "chọn k phần tử"],
        ),
        mc(
            "Tổ hợp",
            "medium",
            "Hệ số của x^2 trong khai triển (1 + x)^4 là bao nhiêu?",
            ["4", "6", "8", "12"],
            "6",
            "Theo nhị thức Newton, hệ số của x^2 là C(4, 2) = 6.",
            ["nhị thức newton", "hệ số", "(1+x)^4", "binomial theorem"],
        ),
    ]
)

QUESTION_BANK.extend(
    [
        mc(
            "Phương pháp chứng minh",
            "easy",
            "Chứng minh trực tiếp thường bắt đầu từ đâu?",
            [
                "Từ giả thiết và suy luận dần đến kết luận.",
                "Từ kết luận rồi phủ định giả thiết.",
                "Từ việc thử vài ví dụ ngẫu nhiên.",
                "Từ việc lập bảng chân trị cho mọi bài toán.",
            ],
            "Từ giả thiết và suy luận dần đến kết luận.",
            "Đây là cách chứng minh tự nhiên nhất: dùng các định nghĩa, định lý và phép biến đổi hợp lệ để đi đến điều cần chứng minh.",
            ["chứng minh trực tiếp", "direct proof", "giả thiết kết luận", "suy luận"],
        ),
        sa(
            "Phương pháp chứng minh",
            "easy",
            "Chứng minh phản chứng là gì?",
            "Chứng minh phản chứng là giả sử kết luận sai rồi suy ra mâu thuẫn, từ đó kết luận mệnh đề ban đầu đúng.",
            "Phương pháp này hữu ích khi khó đi thẳng từ giả thiết đến kết luận.",
            ["phản chứng", "proof by contradiction", "mâu thuẫn", "chứng minh"],
        ),
        essay(
            "Phương pháp chứng minh",
            "medium",
            "Trình bày các bước của chứng minh quy nạp toán học.",
            "Chứng minh quy nạp thường có hai bước. Bước cơ sở: kiểm tra mệnh đề đúng với giá trị nhỏ nhất của n. Bước quy nạp: giả sử mệnh đề đúng với n = k, rồi chứng minh nó đúng với n = k + 1. Khi cả hai bước đều hoàn thành, mệnh đề đúng với mọi n trong miền xét.",
            "Ý tưởng cốt lõi của quy nạp là tạo hiệu ứng dây chuyền: đúng ở điểm bắt đầu và đúng từ k sang k + 1 thì đúng cho mọi giá trị tiếp theo.",
            ["quy nạp", "induction", "bước cơ sở", "bước quy nạp"],
        ),
        mc(
            "Phương pháp chứng minh",
            "easy",
            "Trong chứng minh quy nạp, bước cơ sở dùng để làm gì?",
            [
                "Kiểm tra mệnh đề đúng tại giá trị đầu tiên.",
                "Chứng minh mệnh đề đúng với mọi số nguyên cùng lúc.",
                "Tìm phản ví dụ cho mệnh đề.",
                "Biến đổi kết luận thành giả thiết.",
            ],
            "Kiểm tra mệnh đề đúng tại giá trị đầu tiên.",
            "Nếu không có bước cơ sở thì chuỗi suy luận quy nạp không có điểm khởi đầu.",
            ["bước cơ sở", "base case", "quy nạp", "giá trị đầu tiên"],
        ),
        sa(
            "Phương pháp chứng minh",
            "easy",
            "Mệnh đề phản chứng của p → q là gì?",
            "Mệnh đề phản chứng của p → q là ¬q → ¬p.",
            "Mệnh đề này tương đương logic với mệnh đề gốc nên thường được dùng để chứng minh thay cho p → q.",
            ["phản chứng", "contrapositive", "p q", "logic tương đương"],
        ),
        essay(
            "Phương pháp chứng minh",
            "medium",
            "Quy nạp mạnh khác quy nạp thường ở điểm nào?",
            "Trong quy nạp thường, ở bước quy nạp ta giả sử mệnh đề đúng với một giá trị k rồi chứng minh cho k + 1. Trong quy nạp mạnh, ta được giả sử mệnh đề đúng với mọi giá trị từ điểm đầu đến k để chứng minh cho k + 1. Quy nạp mạnh đặc biệt hữu ích khi trường hợp k + 1 phụ thuộc vào nhiều giá trị trước đó.",
            "Hai phương pháp là tương đương về sức mạnh, nhưng quy nạp mạnh thường thuận tiện hơn cho các bài toán đệ quy hoặc phân tích cấu trúc.",
            ["quy nạp mạnh", "strong induction", "khác nhau", "đệ quy"],
        ),
        mc(
            "Phương pháp chứng minh",
            "easy",
            "Một phản ví dụ có thể làm gì với mệnh đề 'mọi phần tử đều có tính chất P'?",
            [
                "Chứng minh mệnh đề đúng.",
                "Bác bỏ mệnh đề.",
                "Biến mệnh đề thành hằng đúng.",
                "Không có tác dụng gì.",
            ],
            "Bác bỏ mệnh đề.",
            "Chỉ cần một trường hợp không thỏa mãn là đủ để mệnh đề mang lượng từ 'mọi' trở thành sai.",
            ["phản ví dụ", "counterexample", "bác bỏ", "mọi phần tử"],
        ),
        sa(
            "Phương pháp chứng minh",
            "medium",
            "Điều kiện cần và điều kiện đủ khác nhau như thế nào?",
            "A là điều kiện đủ cho B nếu A xảy ra thì kéo theo B. A là điều kiện cần cho B nếu B chỉ có thể xảy ra khi A xảy ra.",
            "Nhiều nhầm lẫn trong chứng minh đến từ việc đảo ngược điều kiện cần và điều kiện đủ.",
            ["điều kiện cần", "điều kiện đủ", "necessary", "sufficient"],
        ),
        essay(
            "Phương pháp chứng minh",
            "medium",
            "So sánh chứng minh trực tiếp, phản chứng và quy nạp toán học.",
            "Chứng minh trực tiếp đi từ giả thiết đến kết luận nên thường ngắn gọn và tự nhiên. Phản chứng giả sử mệnh đề sai rồi dẫn tới mâu thuẫn, phù hợp khi kết luận khó đạt được trực tiếp. Quy nạp toán học dùng cho các mệnh đề phụ thuộc vào số tự nhiên hoặc cấu trúc đệ quy, dựa trên bước cơ sở và bước truyền.",
            "Chọn đúng phương pháp sẽ giúp lời giải sáng rõ và ngắn hơn đáng kể.",
            ["so sánh phương pháp chứng minh", "trực tiếp", "phản chứng", "quy nạp"],
        ),
        mc(
            "Phương pháp chứng minh",
            "easy",
            "Mệnh đề nào sau đây là đúng?",
            [
                "Tổng của hai số chẵn luôn là số lẻ.",
                "Tổng của hai số chẵn luôn là số chẵn.",
                "Tổng của hai số chẵn có thể là số nguyên tố bất kỳ.",
                "Không thể kết luận gì về tổng của hai số chẵn.",
            ],
            "Tổng của hai số chẵn luôn là số chẵn.",
            "Nếu a = 2m và b = 2n thì a + b = 2(m + n), nên tổng vẫn chia hết cho 2.",
            ["số chẵn", "tính chẵn lẻ", "parity", "ví dụ chứng minh"],
        ),
        mc(
            "Quan hệ",
            "easy",
            "Quan hệ R trên tập A được gọi là phản xạ khi nào?",
            [
                "Với mọi a thuộc A, ta có (a, a) thuộc R.",
                "Với mọi a, b thuộc A, nếu (a, b) thuộc R thì (b, a) thuộc R.",
                "Với mọi a, b, c thuộc A, nếu (a, b) và (b, c) thuộc R thì (a, c) thuộc R.",
                "Không tồn tại cặp nào thuộc R.",
            ],
            "Với mọi a thuộc A, ta có (a, a) thuộc R.",
            "Tính phản xạ yêu cầu mỗi phần tử phải liên hệ với chính nó.",
            ["quan hệ phản xạ", "reflexive", "(a,a)", "relation"],
        ),
        sa(
            "Quan hệ",
            "easy",
            "Quan hệ đối xứng là gì?",
            "Quan hệ R là đối xứng nếu khi (a, b) thuộc R thì (b, a) cũng thuộc R.",
            "Tính đối xứng phản ánh việc quan hệ không phụ thuộc thứ tự giữa hai phần tử.",
            ["đối xứng", "symmetric relation", "quan hệ", "a b"],
        ),
        essay(
            "Quan hệ",
            "medium",
            "Trình bày quan hệ tương đương và cho một ví dụ.",
            "Quan hệ tương đương là quan hệ thỏa ba tính chất: phản xạ, đối xứng và bắc cầu. Ví dụ, quan hệ đồng dư modulo n trên tập số nguyên là một quan hệ tương đương vì mỗi số đồng dư với chính nó, nếu a đồng dư b thì b đồng dư a, và nếu a đồng dư b, b đồng dư c thì a đồng dư c.",
            "Quan hệ tương đương giúp chia tập thành các lớp tương đương, mỗi lớp gom những phần tử 'giống nhau' theo một tiêu chí nào đó.",
            ["quan hệ tương đương", "equivalence relation", "đồng dư", "lớp tương đương"],
        ),
        mc(
            "Quan hệ",
            "medium",
            "Quan hệ chia hết trên tập số nguyên dương có tính phản đối xứng không?",
            [
                "Có, vì nếu a | b và b | a thì a = b.",
                "Không, vì a | b luôn kéo theo b | a.",
                "Không, vì quan hệ chia hết không phản xạ.",
                "Không xác định được.",
            ],
            "Có, vì nếu a | b và b | a thì a = b.",
            "Trên tập số nguyên dương, chia hết là ví dụ quen thuộc của quan hệ thứ tự bộ phận.",
            ["phản đối xứng", "antisymmetric", "chia hết", "partial order"],
        ),
        sa(
            "Quan hệ",
            "easy",
            "Quan hệ bắc cầu là gì?",
            "Quan hệ R là bắc cầu nếu từ (a, b) thuộc R và (b, c) thuộc R suy ra (a, c) thuộc R.",
            "Tính bắc cầu cho phép nối hai bước liên hệ thành một bước trực tiếp.",
            ["bắc cầu", "transitive", "quan hệ", "a b c"],
        ),
        essay(
            "Quan hệ",
            "medium",
            "Thế nào là quan hệ thứ tự bộ phận và sơ đồ Hasse dùng để làm gì?",
            "Quan hệ thứ tự bộ phận là quan hệ phản xạ, phản đối xứng và bắc cầu. Sơ đồ Hasse là cách biểu diễn trực quan một poset bằng cách bỏ các cạnh phản xạ và các cạnh có thể suy ra nhờ bắc cầu, giúp ta nhìn rõ cấu trúc bao phủ giữa các phần tử.",
            "Sơ đồ Hasse đặc biệt hữu ích khi so sánh các phần tử theo quan hệ chia hết hoặc bao hàm tập hợp.",
            ["thứ tự bộ phận", "poset", "hasse", "bao phủ"],
        ),
        mc(
            "Quan hệ",
            "medium",
            "Trong ma trận biểu diễn quan hệ R trên tập {a1, a2, ..., an}, phần tử ở hàng i cột j bằng 1 khi nào?",
            [
                "Khi ai = aj.",
                "Khi (ai, aj) thuộc R.",
                "Khi ai không thuộc tập gốc.",
                "Khi j > i.",
            ],
            "Khi (ai, aj) thuộc R.",
            "Ma trận quan hệ là cách mã hóa cặp có thứ tự bằng giá trị 0 và 1.",
            ["ma trận quan hệ", "relation matrix", "hàng cột", "0 1"],
        ),
        sa(
            "Quan hệ",
            "medium",
            "Lớp tương đương của phần tử a là gì?",
            "Lớp tương đương của a là tập gồm tất cả các phần tử b sao cho b có quan hệ tương đương với a.",
            "Các lớp tương đương tạo thành một phân hoạch của tập ban đầu.",
            ["lớp tương đương", "equivalence class", "phân hoạch", "quan hệ"],
        ),
        essay(
            "Quan hệ",
            "medium",
            "So sánh quan hệ tương đương và quan hệ thứ tự bộ phận.",
            "Quan hệ tương đương dùng để gom các phần tử thành các nhóm 'tương đương' và cần ba tính chất phản xạ, đối xứng, bắc cầu. Quan hệ thứ tự bộ phận dùng để so sánh theo kiểu 'nhỏ hơn hoặc bằng' và cần phản xạ, phản đối xứng, bắc cầu. Điểm khác biệt chính là đối xứng của quan hệ tương đương được thay bằng phản đối xứng trong poset.",
            "Hai loại quan hệ này đều rất quan trọng vì chúng mô hình hóa hai kiểu cấu trúc khác nhau: phân loại và sắp thứ tự.",
            ["so sánh quan hệ", "equivalence vs poset", "đối xứng", "phản đối xứng"],
        ),
        mc(
            "Quan hệ",
            "medium",
            "Có bao nhiêu quan hệ nhị phân trên một tập có 2 phần tử?",
            ["4", "8", "16", "32"],
            "16",
            "Một quan hệ nhị phân là một tập con của A × A. Nếu |A| = 2 thì |A × A| = 4, nên có 2^4 = 16 quan hệ.",
            ["đếm quan hệ", "binary relation", "2 mũ n bình", "A x A"],
        ),
    ]
)


def build_aliases(question: str, keywords: list[str], topic: str) -> list[str]:
    aliases = [question, f"giải thích {topic.lower()}", f"ôn tập {topic.lower()}"]
    for keyword in keywords[:2]:
        aliases.append(f"định nghĩa {keyword}")
        aliases.append(f"cho ví dụ về {keyword}")

    deduped = []
    seen = set()
    for alias in aliases:
        normalized = " ".join(alias.strip().split())
        if normalized and normalized not in seen:
            seen.add(normalized)
            deduped.append(normalized)
    return deduped[:6]


def enrich_questions() -> list[dict]:
    enriched = []
    for idx, item in enumerate(QUESTION_BANK, start=1):
        question = dict(item)
        question["id"] = idx
        question["sample_user_questions"] = build_aliases(
            question["question"], question.get("keywords", []), question["topic"]
        )
        enriched.append(question)
    return enriched


def validate_question_bank(questions: list[dict]) -> None:
    if len(questions) != 100:
        raise ValueError(f"Expected 100 questions, found {len(questions)}")

    seen_ids = set()
    for question in questions:
        question_id = question["id"]
        if question_id in seen_ids:
            raise ValueError(f"Duplicate question id: {question_id}")
        seen_ids.add(question_id)

        if question["type"] == "multiple_choice":
            options = question.get("options") or []
            if len(options) < 4:
                raise ValueError(f"Question {question_id} must have at least 4 options")
            if question["answer"] not in options:
                raise ValueError(f"Question {question_id} answer must be one of the options")


def slugify(value: str) -> str:
    return (
        value.lower()
        .replace("đ", "d")
        .replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
    )


def format_question_card(question: dict) -> str:
    sections = [f"Câu hỏi: {question['question']}"]
    options = question.get("options") or []
    if options:
        option_text = "\n".join(f"- {option}" for option in options)
        sections.append(f"Lựa chọn:\n{option_text}")
    sections.append(f"Đáp án: {question['answer']}")
    explanation = question.get("explanation", "").strip()
    if explanation:
        sections.append(f"Giải thích: {explanation}")
    return "\n".join(sections)


def build_knowledge_base(questions: list[dict]) -> list[dict]:
    questions_by_topic: dict[str, list[dict]] = defaultdict(list)
    for question in questions:
        questions_by_topic[question["topic"]].append(question)

    knowledge_items = []
    for topic, topic_questions in questions_by_topic.items():
        blueprint = TOPIC_BLUEPRINTS[topic]
        source_question_ids = [question["id"] for question in topic_questions]
        topic_slug = slugify(topic)

        structured_sections = [
            ("concept_note", blueprint["concept_note"]),
            ("formula_rule", "\n".join(f"- {line}" for line in blueprint["formula_rule"])),
            ("worked_example", blueprint["worked_example"]),
            ("common_mistake", blueprint["common_mistake"]),
            ("exercise_variants", "\n".join(f"- {line}" for line in blueprint["exercise_variants"])),
        ]

        for kind, content in structured_sections:
            knowledge_items.append(
                {
                    "id": f"{topic_slug}::{kind}",
                    "topic": topic,
                    "kind": kind,
                    "title": f"{topic} - {kind}",
                    "content": content,
                    "keywords": blueprint["keywords"],
                    "difficulty": "mixed",
                    "source_question_ids": source_question_ids,
                }
            )

        for question in topic_questions:
            card_keywords = list(
                dict.fromkeys(
                    (question.get("keywords") or []) + (question.get("sample_user_questions") or [])
                )
            )
            knowledge_items.append(
                {
                    "id": f"question_card::{question['id']}",
                    "topic": question["topic"],
                    "kind": "question_card",
                    "title": question["question"],
                    "content": format_question_card(question),
                    "keywords": card_keywords,
                    "difficulty": question["difficulty"],
                    "source_question_ids": [question["id"]],
                }
            )

    return knowledge_items


def validate_knowledge_base(knowledge_items: list[dict], questions: list[dict]) -> None:
    expected_topics = {question["topic"] for question in questions}
    actual_topics = {item["topic"] for item in knowledge_items}
    if expected_topics != actual_topics:
        missing_topics = sorted(expected_topics - actual_topics)
        raise ValueError(f"Knowledge base is missing topics: {missing_topics}")

    seen_ids = set()
    for item in knowledge_items:
        if item["id"] in seen_ids:
            raise ValueError(f"Duplicate knowledge item id: {item['id']}")
        seen_ids.add(item["id"])


def main() -> None:
    questions = enrich_questions()
    validate_question_bank(questions)
    knowledge_items = build_knowledge_base(questions)
    validate_knowledge_base(knowledge_items, questions)
    OUTPUT_PATH.write_text(
        json.dumps(questions, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    KNOWLEDGE_OUTPUT_PATH.write_text(
        json.dumps(knowledge_items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(
        f"Created {len(questions)} questions at {OUTPUT_PATH} "
        f"and {len(knowledge_items)} knowledge items at {KNOWLEDGE_OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
