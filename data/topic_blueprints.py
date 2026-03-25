TOPIC_BLUEPRINTS = {
    "Tập hợp": {
        "keywords": ["tập hợp", "tập con", "hợp", "giao", "hiệu", "lực lượng", "power set"],
        "concept_note": (
            "Tập hợp là mô hình dùng để gom các đối tượng xác định rõ ràng. Khi học phần này, cần nhớ hai ý chính: "
            "một phần tử hoặc thuộc tập hoặc không thuộc tập, và thứ tự lặp lại của phần tử không làm thay đổi tập hợp. "
            "Các phép toán như hợp, giao, hiệu và phần bù giúp ta mô tả cách kết hợp hoặc loại trừ thông tin giữa nhiều tập."
        ),
        "formula_rule": [
            "Nếu |A| = n thì |P(A)| = 2^n.",
            "|A ∪ B| = |A| + |B| - |A ∩ B|.",
            "(A ∪ B)^c = A^c ∩ B^c và (A ∩ B)^c = A^c ∪ B^c."
        ],
        "worked_example": (
            "Ví dụ: với A = {1, 2, 3} và B = {2, 3, 4}, ta có A ∪ B = {1, 2, 3, 4}, "
            "A ∩ B = {2, 3}, và A \\ B = {1}. Từ ví dụ này có thể thấy hợp là gộp, giao là phần chung, "
            "còn hiệu là phần thuộc A nhưng không thuộc B."
        ),
        "common_mistake": (
            "Lỗi hay gặp là đếm trùng phần tử khi lấy hợp, hoặc nhầm A \\ B với B \\ A. "
            "Khi gặp bài đếm, nên viết rõ từng tập trung gian trước khi kết luận."
        ),
        "exercise_variants": [
            "Cho hai tập A, B. Hãy tính A ∪ B, A ∩ B và A \\ B.",
            "Một tập có n phần tử thì có bao nhiêu tập con?",
            "Dùng định luật De Morgan để biến đổi biểu thức tập hợp."
        ],
    },
    "Logic mệnh đề": {
        "keywords": ["mệnh đề", "kéo theo", "tương đương", "phủ định", "bảng chân trị", "lượng từ"],
        "concept_note": (
            "Logic mệnh đề nghiên cứu các câu khẳng định có chân trị đúng hoặc sai và cách kết hợp chúng bằng các phép nối logic. "
            "Mấu chốt là hiểu nghĩa của từng phép như phủ định, hội, tuyển, kéo theo, tương đương và biết kiểm tra tính đúng sai bằng lập luận hoặc bảng chân trị."
        ),
        "formula_rule": [
            "p → q chỉ sai khi p đúng và q sai.",
            "¬(p ∧ q) ≡ ¬p ∨ ¬q; ¬(p ∨ q) ≡ ¬p ∧ ¬q.",
            "Phản chứng của p → q là ¬q → ¬p và luôn tương đương logic với mệnh đề gốc."
        ],
        "worked_example": (
            "Ví dụ: mệnh đề 'Nếu một số chia hết cho 4 thì nó chẵn' có dạng p → q. "
            "Ta không cần q kéo theo p; điều quan trọng là chỉ cần chứng minh mọi trường hợp p đúng thì q cũng đúng."
        ),
        "common_mistake": (
            "Sinh viên thường nhầm mệnh đề đảo q → p với phản chứng ¬q → ¬p. "
            "Ngoài ra cũng hay quên rằng kéo theo không sai khi tiền đề p sai."
        ),
        "exercise_variants": [
            "Lập bảng chân trị cho biểu thức logic đã cho.",
            "Tìm phủ định của mệnh đề chứa lượng từ.",
            "Phân biệt mệnh đề đảo, phản đảo và phản chứng trong một phát biểu cụ thể."
        ],
    },
    "Quan hệ": {
        "keywords": ["quan hệ", "phản xạ", "đối xứng", "phản đối xứng", "bắc cầu", "tương đương", "thứ tự"],
        "concept_note": (
            "Quan hệ trên một tập mô tả cách các phần tử liên hệ với nhau. Khi phân tích quan hệ, ta thường kiểm tra các tính chất như phản xạ, đối xứng, phản đối xứng và bắc cầu để xác định nó là quan hệ tương đương hay quan hệ thứ tự."
        ),
        "formula_rule": [
            "Quan hệ tương đương phải phản xạ, đối xứng và bắc cầu.",
            "Quan hệ thứ tự bộ phận phải phản xạ, phản đối xứng và bắc cầu.",
            "Ma trận quan hệ và đồ thị có hướng là hai cách biểu diễn quen thuộc của quan hệ."
        ],
        "worked_example": (
            "Ví dụ: trên tập số nguyên, quan hệ 'a ≡ b (mod 3)' là quan hệ tương đương vì luôn phản xạ, đối xứng và bắc cầu. "
            "Các lớp tương đương là [0], [1], [2] theo modulo 3."
        ),
        "common_mistake": (
            "Lỗi phổ biến là nhầm phản đối xứng với không đối xứng. "
            "Phản đối xứng cho phép aRb và bRa cùng xảy ra, nhưng khi đó phải suy ra a = b."
        ),
        "exercise_variants": [
            "Kiểm tra một quan hệ có phải quan hệ tương đương hay không.",
            "Xác định một quan hệ có phải thứ tự bộ phận hay không.",
            "Viết ma trận hoặc đồ thị biểu diễn một quan hệ cho trước."
        ],
    },
    "Hàm": {
        "keywords": ["hàm", "đơn ánh", "toàn ánh", "song ánh", "hàm ngược", "miền xác định", "đồng miền"],
        "concept_note": (
            "Hàm là quy tắc gán mỗi phần tử của miền xác định đúng một phần tử ở đồng miền. "
            "Trong Toán rời rạc, ta đặc biệt quan tâm đến đơn ánh, toàn ánh, song ánh và việc đếm số hàm giữa các tập hữu hạn."
        ),
        "formula_rule": [
            "Số hàm từ tập có m phần tử sang tập có n phần tử là n^m.",
            "Đơn ánh nghĩa là hai đầu vào khác nhau cho hai đầu ra khác nhau.",
            "Song ánh là vừa đơn ánh vừa toàn ánh, khi đó hàm ngược tồn tại."
        ],
        "worked_example": (
            "Ví dụ: từ tập A có 3 phần tử sang tập B có 2 phần tử sẽ có 2^3 = 8 hàm. "
            "Nếu muốn hàm song ánh thì hai tập phải có cùng số phần tử và mỗi phần tử của B được nhận đúng một lần."
        ),
        "common_mistake": (
            "Hay nhầm giữa codomain và image, dẫn đến kết luận sai về toàn ánh. "
            "Khi xét toàn ánh, cần kiểm tra mọi phần tử của đồng miền đều được ánh xạ tới."
        ),
        "exercise_variants": [
            "Đếm số hàm từ A sang B với |A| = m, |B| = n.",
            "Kiểm tra một hàm có đơn ánh hoặc toàn ánh hay không.",
            "Tìm điều kiện để một hàm có hàm ngược."
        ],
    },
    "Tổ hợp": {
        "keywords": ["tổ hợp", "hoán vị", "chỉnh hợp", "quy tắc cộng", "quy tắc nhân", "nhị thức Newton"],
        "concept_note": (
            "Tổ hợp giúp đếm số cách chọn, sắp xếp hoặc phân bố đối tượng mà không cần liệt kê từng trường hợp. "
            "Muốn giải tốt, trước tiên phải xác định bài toán đang đếm theo thứ tự hay không và có cho phép lặp lại hay không."
        ),
        "formula_rule": [
            "Hoán vị n phần tử: n!.",
            "Chỉnh hợp chập k của n phần tử: A(n, k) = n! / (n-k)!.",
            "Tổ hợp chập k của n phần tử: C(n, k) = n! / (k!(n-k)!)."
        ],
        "worked_example": (
            "Ví dụ: chọn 2 sinh viên từ nhóm 5 sinh viên là C(5, 2) = 10 vì thứ tự không quan trọng. "
            "Nếu xếp 2 sinh viên đó vào hai vị trí khác nhau thì phải dùng chỉnh hợp A(5, 2) = 20."
        ),
        "common_mistake": (
            "Lỗi điển hình là dùng hoán vị trong khi bài chỉ cần chọn nhóm, hoặc quên chia cho số cách hoán đổi khi thứ tự không quan trọng."
        ),
        "exercise_variants": [
            "Phân biệt khi nào dùng hoán vị, chỉnh hợp, tổ hợp.",
            "Đếm số cách chọn k phần tử từ n phần tử.",
            "Giải bài toán đếm bằng quy tắc cộng và quy tắc nhân."
        ],
    },
    "Phương pháp chứng minh": {
        "keywords": ["chứng minh", "trực tiếp", "phản chứng", "quy nạp", "phản ví dụ", "mệnh đề"],
        "concept_note": (
            "Phương pháp chứng minh là bộ công cụ để chuyển trực giác thành lập luận chặt chẽ. "
            "Trong Toán rời rạc, các kỹ thuật quan trọng nhất là chứng minh trực tiếp, phản chứng, phản ví dụ và quy nạp toán học."
        ),
        "formula_rule": [
            "Chứng minh trực tiếp đi từ giả thiết đến kết luận bằng chuỗi suy luận hợp lệ.",
            "Phản chứng giả sử kết luận sai rồi dẫn đến mâu thuẫn.",
            "Quy nạp gồm bước cơ sở và bước quy nạp n → n+1."
        ],
        "worked_example": (
            "Ví dụ: để chứng minh tổng n số lẻ đầu tiên bằng n^2, ta kiểm tra n = 1 đúng, sau đó giả sử đúng với n = k và chứng minh đúng với n = k + 1 bằng cách cộng thêm số lẻ tiếp theo 2k + 1."
        ),
        "common_mistake": (
            "Lỗi thường gặp là bước quy nạp chỉ lặp lại giả thiết mà không thật sự suy ra trường hợp k + 1, hoặc dùng phản chứng nhưng không chỉ rõ mâu thuẫn xuất hiện ở đâu."
        ),
        "exercise_variants": [
            "Chứng minh một đẳng thức bằng quy nạp toán học.",
            "Dùng phản chứng để bác bỏ một khẳng định.",
            "Chỉ ra phản ví dụ cho một phát biểu sai."
        ],
    },
    "Hệ thức truy hồi": {
        "keywords": ["truy hồi", "fibonacci", "cấp số", "nghiệm tổng quát", "điều kiện đầu", "dãy"],
        "concept_note": (
            "Hệ thức truy hồi mô tả một dãy thông qua các giá trị trước đó. "
            "Để giải bài, ta cần nhận dạng bậc của truy hồi, điều kiện đầu và loại quan hệ: tuyến tính, thuần nhất hay không thuần nhất."
        ),
        "formula_rule": [
            "Muốn xác định duy nhất dãy truy hồi bậc k cần k điều kiện đầu phù hợp.",
            "Fibonacci: F_n = F_{n-1} + F_{n-2}, với F_0 = 0, F_1 = 1.",
            "Cấp số cộng có thể viết a_n = a_{n-1} + d."
        ],
        "worked_example": (
            "Ví dụ: với a_n = a_{n-1} + 3 và a_1 = 2, ta lần lượt có a_2 = 5, a_3 = 8, rồi suy ra công thức tường minh a_n = 2 + 3(n-1)."
        ),
        "common_mistake": (
            "Nhiều bạn chỉ lặp vài bước đầu rồi kết luận luôn mà không chỉ ra vì sao công thức tổng quát đúng. "
            "Khi giải truy hồi, nên tách rõ phần đoán công thức và phần kiểm chứng."
        ),
        "exercise_variants": [
            "Tìm vài số hạng đầu của một dãy truy hồi.",
            "Tìm công thức tường minh của cấp số truy hồi đơn giản.",
            "Giải thích ý nghĩa của điều kiện đầu trong hệ thức truy hồi."
        ],
    },
    "Lý thuyết đồ thị": {
        "keywords": ["đồ thị", "đỉnh", "cạnh", "đường đi", "chu trình", "liên thông", "bậc"],
        "concept_note": (
            "Đồ thị là công cụ mô hình hóa các đối tượng và mối liên kết giữa chúng. "
            "Trong học phần cơ bản, ta thường phân tích bậc đỉnh, đường đi, chu trình, liên thông, đồ thị đầy đủ và đồ thị hai phía."
        ),
        "formula_rule": [
            "Tổng bậc của các đỉnh trong đồ thị vô hướng bằng 2 lần số cạnh.",
            "Đồ thị liên thông là đồ thị có đường đi giữa mọi cặp đỉnh.",
            "Đồ thị hai phía không chứa chu trình độ dài lẻ."
        ],
        "worked_example": (
            "Ví dụ: nếu một đồ thị vô hướng có 5 cạnh thì tổng bậc các đỉnh bằng 10. "
            "Thông tin này thường giúp ta kiểm tra nhanh dữ liệu đề bài hoặc suy ra bậc của đỉnh còn thiếu."
        ),
        "common_mistake": (
            "Hay nhầm đường đi với chu trình, hoặc đếm sai bậc khi có khuyên và cạnh lặp. "
            "Khi đọc đề, nên xác định rõ đồ thị vô hướng hay có hướng trước khi tính."
        ),
        "exercise_variants": [
            "Tính bậc các đỉnh và số cạnh của đồ thị.",
            "Xác định đồ thị có liên thông hay không.",
            "Phân biệt đường đi, chu trình và đồ thị hai phía trong ví dụ cụ thể."
        ],
    },
    "Cây": {
        "keywords": ["cây", "lá", "cây có gốc", "spanning tree", "đường đi duy nhất", "n-1 cạnh"],
        "concept_note": (
            "Cây là đồ thị liên thông không chứa chu trình. Đây là cấu trúc đặc biệt quan trọng vì nó vừa đủ để nối mọi đỉnh nhưng không dư cạnh, nên xuất hiện nhiều trong mạng máy tính, cấu trúc dữ liệu và thuật toán."
        ),
        "formula_rule": [
            "Cây có n đỉnh luôn có n - 1 cạnh.",
            "Giữa hai đỉnh bất kỳ của cây có đúng một đường đi đơn.",
            "Trong cây vô hướng, lá là đỉnh có bậc 1."
        ],
        "worked_example": (
            "Ví dụ: nếu một cây có 8 đỉnh thì chắc chắn có 7 cạnh. "
            "Khi thêm một cạnh bất kỳ vào cây, ta tạo ra đúng một chu trình; khi bỏ một cạnh trên chu trình đó đi, ta quay lại một cây."
        ),
        "common_mistake": (
            "Nhiều bạn nhớ 'cây có n-1 cạnh' nhưng quên điều kiện liên thông. "
            "Một đồ thị có n-1 cạnh mà không liên thông thì chưa chắc là cây."
        ),
        "exercise_variants": [
            "Chứng minh một đồ thị là cây bằng các tiêu chuẩn tương đương.",
            "Tính số cạnh của cây khi biết số đỉnh.",
            "Xác định lá, nút cha, nút con trong cây có gốc."
        ],
    },
    "Đại số Boole và thuật toán": {
        "keywords": ["boole", "and", "or", "not", "biểu thức logic", "thuật toán", "độ phức tạp"],
        "concept_note": (
            "Đại số Boole mô tả các giá trị đúng/sai và các phép toán logic cơ bản. "
            "Phần này thường gắn với thuật toán vì điều kiện rẽ nhánh, biểu thức điều kiện và mạch logic đều dựa trên các quy luật Boole."
        ),
        "formula_rule": [
            "x + xy = x và x(x + y) = x là các luật hấp thụ cơ bản.",
            "x + 0 = x, x·1 = x, x + 1 = 1, x·0 = 0.",
            "Luật De Morgan: ¬(x ∧ y) = ¬x ∨ ¬y, ¬(x ∨ y) = ¬x ∧ ¬y."
        ],
        "worked_example": (
            "Ví dụ: x + xy = x vì nếu x = 1 thì cả hai vế đều bằng 1, còn nếu x = 0 thì x + xy = 0 + 0·y = 0. "
            "Ta có thể kiểm tra bằng biến đổi đại số hoặc bảng chân trị."
        ),
        "common_mistake": (
            "Lỗi phổ biến là dùng ký hiệu cộng và nhân theo nghĩa số học thay vì logic. "
            "Trong Boole, 1 + 1 vẫn bằng 1 nếu dấu + đang biểu diễn phép OR."
        ),
        "exercise_variants": [
            "Rút gọn một biểu thức Boole bằng các luật cơ bản.",
            "Lập bảng chân trị cho biểu thức điều kiện.",
            "Giải thích vai trò của biến Boole trong thuật toán và chương trình."
        ],
    },
}
