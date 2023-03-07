// document.getElementById("sortableStock").addEventListener("click", function() {
//     alert("sortableStock");
// });

// document.getElementById("sortableLgtm").addEventListener("click", function() {
//     alert("sortableLgtm");
// });

function convertToNumberIfPossible(value) {
    const parsedValue = Number(value);
    
    return isNaN(parsedValue) ? value : parsedValue;
  }

function sortTable(table, column, asc = true) {
    const tbody = table.tBodies[0];
    const rows = Array.from(tbody.querySelectorAll("tr"));
  
    // データを取得し、比較する関数を定義する
    const compare = (rowA, rowB) => {
        // console.log('rowA.cells[column].textContent.trim(): ', rowA.cells[0].textContent.trim());
        
      const rowDataA = convertToNumberIfPossible(rowA.cells[column].textContent.trim());
      const rowDataB = convertToNumberIfPossible(rowB.cells[column].textContent.trim());
      if (rowDataA < rowDataB) {
        return asc ? -1 : 1;
      } else if (rowDataA > rowDataB) {
        return asc ? 1 : -1;
      } else {
        return 0;
      }
    };

    // 行をソートする
    rows.sort(compare);// 最初の要素以外をソート
    tbody.append(...rows);
  
    // ソート用のクラスを設定する
    table.querySelectorAll(".sortable").forEach((th) => {
      th.classList.remove("sort-up", "sort-down");
      if (th.cellIndex === column) {
        th.classList.toggle("sort-up", asc);
        th.classList.toggle("sort-down", !asc);
      }
    });

    // 1列目(Index)はソートしない
    table.querySelectorAll("tr").forEach((tr, index) => {
        // テーブル要素を取得
        var table = document.getElementById("articlesTable");

        if(index>0){
            var element = table.rows[index].cells[0];
            // 要素の内容を書き換える
            element.textContent = String(index);
        }
    });
  }
  
  // テーブルを取得し、クリックイベントを追加する
  const table = document.getElementById("articlesTable");
  table.querySelectorAll(".sortable").forEach((th) => {

    th.addEventListener("click", () => {
      const column = th.cellIndex;
      const currentIsAscending = th.classList.contains("sort-up");
      sortTable(table, column, !currentIsAscending);
    });
  });
