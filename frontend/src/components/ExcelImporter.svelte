<script>
  import { onMount } from 'svelte';
  import { importAPI } from '../lib/api.js';

  let fileInput;
  let selectedFile = null;
  let error = '';
  let success = '';
  let loading = false;
  let parsedData = null;
  let rangeA5D7 = [];
  let attendanceDates = [];
  let savedDataList = [];
  let showSavedData = false;

  onMount(() => {
    loadSavedData();
  });

  async function loadSavedData() {
    try {
      const response = await importAPI.getAll();
      savedDataList = response.data;
    } catch (err) {
      console.error('保存データの読み込みエラー:', err);
    }
  }

  function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    // HTMLファイルまたはExcelファイルをチェック
    const validTypes = [
      'text/html',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];
    
    if (!validTypes.includes(file.type) && !file.name.endsWith('.html') && !file.name.endsWith('.htm') && !file.name.endsWith('.xls') && !file.name.endsWith('.xlsx')) {
      error = 'HTMLファイル（.html）またはExcelファイル（.xls, .xlsx）を選択してください';
      return;
    }

    selectedFile = file;
    error = '';
    success = '';
  }

  async function importFile() {
    if (!selectedFile) {
      error = 'ファイルを選択してください';
      return;
    }

    loading = true;
    error = '';
    success = '';

    try {
      if (selectedFile.name.endsWith('.html') || selectedFile.name.endsWith('.htm')) {
        // HTMLファイルとして処理
        const fileContent = await readFileAsText(selectedFile);
        parseHTMLExcel(fileContent);
      } else if (selectedFile.name.endsWith('.xls') || selectedFile.name.endsWith('.xlsx')) {
        // Excelファイルとして処理
        const fileContent = await readFileAsArrayBuffer(selectedFile);
        await parseExcelFile(fileContent);
      } else {
        error = 'HTMLファイル（.html）またはExcelファイル（.xls, .xlsx）を選択してください。';
        return;
      }

      success = 'ファイルが正常にインポートされました';
    } catch (err) {
      console.error('Import error:', err);
      error = 'ファイルの読み込みに失敗しました: ' + err.message;
    } finally {
      loading = false;
    }
  }

  async function saveToDatabase() {
    if (!parsedData) {
      error = '保存するデータがありません';
      return;
    }

    loading = true;
    error = '';

    try {
      const saveData = {
        filename: selectedFile ? selectedFile.name : 'unknown',
        basic_info: rangeA5D7,
        attendance_dates: attendanceDates
      };

      await importAPI.saveData(saveData);
      success = 'データがデータベースに保存されました';
      await loadSavedData(); // 保存データリストを更新
    } catch (err) {
      console.error('Save error:', err);
      error = 'データの保存に失敗しました: ' + err.response?.data?.error || err.message;
    } finally {
      loading = false;
    }
  }

  async function loadSavedDataDetail(dataId) {
    try {
      const response = await importAPI.getDetail(dataId);
      const data = response.data;
      
      // 保存されたデータを表示用に設定
      rangeA5D7 = data.basic_info?.range_data || [];
      attendanceDates = data.attendance_dates || [];
      parsedData = {
        totalRows: rangeA5D7.length + attendanceDates.length,
        totalCols: 4,
        isMultiSheet: true,
        savedData: true,
        import_date: data.import_date,
        filename: data.filename
      };
      
      selectedFile = null; // ファイル選択をクリア
      success = `保存データ「${data.filename}」を読み込みました`;
      error = '';
    } catch (err) {
      console.error('Load saved data error:', err);
      error = '保存データの読み込みに失敗しました';
    }
  }

  async function deleteSavedData(dataId) {
    if (!confirm('このデータを削除しますか？')) return;
    
    try {
      await importAPI.delete(dataId);
      success = 'データを削除しました';
      await loadSavedData();
    } catch (err) {
      console.error('Delete error:', err);
      error = 'データの削除に失敗しました';
    }
  }

  function readFileAsText(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(new Error('ファイルの読み込みに失敗しました'));
      reader.readAsText(file, 'utf-8');
    });
  }

  function readFileAsArrayBuffer(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(new Error('ファイルの読み込みに失敗しました'));
      reader.readAsArrayBuffer(file);
    });
  }

  async function parseExcelFile(arrayBuffer) {
    try {
      // SheetJSライブラリを動的に読み込み
      if (typeof XLSX === 'undefined') {
        await loadSheetJS();
      }

      const workbook = XLSX.read(arrayBuffer, { type: 'array' });
      
      console.log('シート数:', workbook.SheetNames.length);
      console.log('シート名一覧:', workbook.SheetNames);
      
      // 複数シートの場合の処理
      if (workbook.SheetNames.length > 1) {
        console.log('複数シート処理を開始');
        
        // Sheet1から基本情報を取得
        const sheet1 = workbook.Sheets[workbook.SheetNames[0]];
        const sheet1Data = XLSX.utils.sheet_to_json(sheet1, { 
          header: 1,
          raw: false,
          defval: ''
        });

        // Sheet2から出勤簿データを取得
        const sheet2 = workbook.Sheets[workbook.SheetNames[1]];
        const sheet2Data = XLSX.utils.sheet_to_json(sheet2, { 
          header: 1,
          raw: false,
          defval: ''
        });

        console.log('Sheet1データ:', sheet1Data);
        console.log('Sheet2データ:', sheet2Data);

        // データを組み合わせて解析
        extractDataFromMultipleSheets(sheet1Data, sheet2Data, workbook.SheetNames);
      } else {
        console.log('単一シート処理を開始');
        // 単一シートの場合は従来の処理
        const firstSheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[firstSheetName];
        
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { 
          header: 1,
          raw: false,
          defval: ''
        });

        console.log('単一シートデータ:', jsonData);
        extractDataFromGrid(jsonData, firstSheetName);
      }

    } catch (err) {
      console.error('Excel解析エラー:', err);
      throw new Error('Excelファイルの解析に失敗しました: ' + err.message);
    }
  }

  function extractDataFromMultipleSheets(sheet1Data, sheet2Data, sheetNames) {
    console.log('複数シートからのデータ抽出を開始');
    
    // Sheet1から基本情報（全行）を取得
    rangeA5D7 = [];
    for (let row = 0; row < sheet1Data.length; row++) {
      if (sheet1Data[row]) {
        const rowData = [];
        for (let col = 0; col <= 3; col++) {
          rowData.push(sheet1Data[row][col] || '');
        }
        rangeA5D7.push(rowData);
      }
    }
    console.log('基本情報データ:', rangeA5D7);

    // Sheet2から出講日を取得（B列の日付データ）
    attendanceDates = [];
    for (let row = 1; row < sheet2Data.length; row++) { // ヘッダー行をスキップ
      if (sheet2Data[row] && sheet2Data[row][1]) { // B列
        const dateText = String(sheet2Data[row][1]).trim();
        if (dateText && dateText !== '' && dateText !== '出講日') {
          console.log('日付チェック:', dateText, 'バリデーション結果:', isValidDateString(dateText));
          // 日付らしい文字列のみを抽出
          if (isValidDateString(dateText)) {
            attendanceDates.push({
              row: row + 1, // 1ベースの行番号
              date: dateText,
              attendance: sheet2Data[row][2] || '', // C列（印）
              checkIn: sheet2Data[row][3] || '',    // D列（出勤時刻）
              checkOut: sheet2Data[row][4] || '',   // E列（退勤時刻）
              hours: sheet2Data[row][5] || '',      // F列（時間数）
              notes: sheet2Data[row][6] || ''       // G列（備考）
            });
          }
        }
      }
    }
    console.log('出講日データ:', attendanceDates);

    parsedData = {
      totalRows: sheet1Data.length + sheet2Data.length,
      totalCols: Math.max(
        Math.max(...sheet1Data.map(row => row?.length || 0)),
        Math.max(...sheet2Data.map(row => row?.length || 0))
      ),
      rangeA5D7,
      attendanceDates,
      sheetNames: sheetNames,
      sheet1Rows: sheet1Data.length,
      sheet2Rows: sheet2Data.length,
      isMultiSheet: true // 複数シートフラグ
    };
    
    console.log('最終データ:', parsedData);
  }

  function parseHTMLExcel(htmlContent) {
    // HTMLを解析してテーブルデータを抽出
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlContent, 'text/html');
    
    // テーブルを探す
    const tables = doc.querySelectorAll('table');
    if (tables.length === 0) {
      throw new Error('テーブルが見つかりませんでした');
    }

    // 最初のテーブルを使用（複数ある場合は最大のものを選択）
    let targetTable = tables[0];
    if (tables.length > 1) {
      let maxRows = 0;
      tables.forEach(table => {
        const rows = table.querySelectorAll('tr');
        if (rows.length > maxRows) {
          maxRows = rows.length;
          targetTable = table;
        }
      });
    }

    const rows = Array.from(targetTable.querySelectorAll('tr'));
    
    // セルのデータを2次元配列に変換
    const cellData = [];
    rows.forEach((row, rowIndex) => {
      const cells = Array.from(row.querySelectorAll('td, th'));
      const rowData = [];
      cells.forEach(cell => {
        // セルの内容を取得（改行や空白を整理）
        let content = cell.textContent || cell.innerText || '';
        content = content.trim().replace(/\s+/g, ' ');
        rowData.push(content);
      });
      cellData.push(rowData);
    });

    extractDataFromGrid(cellData);
  }

  function extractDataFromGrid(gridData, sheetName = null) {
    // A5-D7の範囲を抽出（0ベースなので4-6行目、0-3列目）
    rangeA5D7 = [];
    for (let row = 4; row <= 6; row++) {
      if (gridData[row]) {
        const rowData = [];
        for (let col = 0; col <= 3; col++) {
          rowData.push(gridData[row][col] || '');
        }
        rangeA5D7.push(rowData);
      }
    }

    // B11以降の出講日を抽出（0ベースなので10行目以降、1列目）
    attendanceDates = [];
    for (let row = 10; row < gridData.length; row++) {
      if (gridData[row] && gridData[row][1]) {
        const dateText = String(gridData[row][1]).trim();
        if (dateText && dateText !== '') {
          // 日付らしい文字列のみを抽出
          if (isValidDateString(dateText)) {
            attendanceDates.push({
              row: row + 1, // 1ベースの行番号
              date: dateText
            });
          }
        }
      }
    }

    parsedData = {
      totalRows: gridData.length,
      totalCols: Math.max(...gridData.map(row => row?.length || 0)),
      rangeA5D7,
      attendanceDates,
      sheetName
    };
  }

  function loadSheetJS() {
    return new Promise((resolve, reject) => {
      if (typeof XLSX !== 'undefined') {
        resolve();
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('SheetJSライブラリの読み込みに失敗しました'));
      document.head.appendChild(script);
    });
  }

  function isValidDateString(str) {
    // 日付っぽい文字列を判定（2025-04-08形式を優先）
    const datePatterns = [
      /^\d{4}-\d{1,2}-\d{1,2}$/,               // 2025-04-08 (推奨形式)
      /^\d{4}[\/]\d{1,2}[\/]\d{1,2}$/,        // 2025/04/08
      /^\d{1,2}[\/]\d{1,2}[\/]\d{4}$/,        // 04/08/2025
      /^\d{1,2}[\/]\d{1,2}$/,                 // 04/08
      /^\d{4}年\d{1,2}月\d{1,2}日$/,          // 2025年04月08日
      /^\d{1,2}月\d{1,2}日$/,                 // 04月08日
      /^[0-9]{1,2}月[0-9]{1,2}日$/            // 4月8日
    ];
    
    return datePatterns.some(pattern => pattern.test(str));
  }

  function reset() {
    selectedFile = null;
    parsedData = null;
    rangeA5D7 = [];
    attendanceDates = [];
    error = '';
    success = '';
    if (fileInput) {
      fileInput.value = '';
    }
  }

  function downloadSample() {
    // サンプルHTMLファイルを生成してダウンロード
    const sampleHTML = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>勤怠管理サンプル</title>
</head>
<body>
    <table border="1">
        <tr><td>A1</td><td>B1</td><td>C1</td><td>D1</td></tr>
        <tr><td>A2</td><td>B2</td><td>C2</td><td>D2</td></tr>
        <tr><td>A3</td><td>B3</td><td>C3</td><td>D3</td></tr>
        <tr><td>A4</td><td>B4</td><td>C4</td><td>D4</td></tr>
        <tr><td>氏名</td><td>山田太郎</td><td>部署</td><td>開発部</td></tr>
        <tr><td>社員番号</td><td>12345</td><td>役職</td><td>主任</td></tr>
        <tr><td>入社日</td><td>2020/04/01</td><td>連絡先</td><td>yamada@example.com</td></tr>
        <tr><td>A8</td><td>B8</td><td>C8</td><td>D8</td></tr>
        <tr><td>A9</td><td>B9</td><td>C9</td><td>D9</td></tr>
        <tr><td>A10</td><td>B10</td><td>C10</td><td>D10</td></tr>
        <tr><td>出講日</td><td>2024/01/15</td><td></td><td></td></tr>
        <tr><td></td><td>2024/01/16</td><td></td><td></td></tr>
        <tr><td></td><td>2024/01/17</td><td></td><td></td></tr>
        <tr><td></td><td>2024/01/22</td><td></td><td></td></tr>
        <tr><td></td><td>2024/01/23</td><td></td><td></td></tr>
    </table>
</body>
</html>`;

    const blob = new Blob([sampleHTML], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_attendance.html';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
</script>

<div class="excel-importer">
  <div class="card">
    <h2>Excelファイルインポート</h2>
    
    {#if error}
      <p class="error">{error}</p>
    {/if}
    
    {#if success}
      <p class="success">{success}</p>
    {/if}
    
    <div class="file-upload-section">
      <div class="form-group">
        <label for="file-input">ファイル選択（Excel または HTML形式のファイル）</label>
        <input 
          bind:this={fileInput}
          id="file-input"
          type="file" 
          accept=".html,.htm,.xls,.xlsx"
          on:change={handleFileSelect}
          disabled={loading}
        />
        <small class="file-help">対応形式: .xls, .xlsx, .html, .htm</small>
      </div>
      
      <div class="button-group">
        <button on:click={importFile} disabled={loading || !selectedFile}>
          {loading ? 'インポート中...' : 'インポート'}
        </button>
        {#if parsedData && !parsedData.savedData}
          <button on:click={saveToDatabase} disabled={loading} class="save-btn">
            {loading ? '保存中...' : 'データベースに保存'}
          </button>
        {/if}
        <button on:click={reset} disabled={loading}>
          リセット
        </button>
        <button on:click={downloadSample} class="sample-btn">
          サンプルファイルダウンロード
        </button>
        <button on:click={() => showSavedData = !showSavedData} class="saved-data-btn">
          {showSavedData ? '保存データを非表示' : '保存データを表示'}
        </button>
      </div>
    </div>
    
    {#if selectedFile}
      <div class="file-info">
        <h4>選択されたファイル</h4>
        <p><strong>ファイル名:</strong> {selectedFile.name}</p>
        <p><strong>サイズ:</strong> {(selectedFile.size / 1024).toFixed(2)} KB</p>
        <p><strong>形式:</strong> {selectedFile.type || '不明'}</p>
      </div>
    {/if}
  </div>

  <!-- 保存データ一覧 -->
  {#if showSavedData}
    <div class="card">
      <h3>保存されたデータ一覧</h3>
      {#if savedDataList.length > 0}
        <table class="data-table">
          <thead>
            <tr>
              <th>ファイル名</th>
              <th>インポート日時</th>
              <th>基本情報</th>
              <th>出講日数</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {#each savedDataList as item}
              <tr>
                <td>{item.filename}</td>
                <td>{new Date(item.import_date).toLocaleString('ja-JP')}</td>
                <td>{item.basic_info?.name || '未設定'}</td>
                <td>{item.attendance_dates?.length || 0}件</td>
                <td>
                  <button on:click={() => loadSavedDataDetail(item.id)} class="load-btn">
                    表示
                  </button>
                  <button on:click={() => deleteSavedData(item.id)} class="delete-btn">
                    削除
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      {:else}
        <p>保存されたデータはありません</p>
      {/if}
    </div>
  {/if}

  {#if parsedData}
    <div class="card">
      <h3>解析結果</h3>
      {#if parsedData.savedData}
        <p class="saved-indicator">💾 データベースから読み込み</p>
        <p><strong>ファイル名:</strong> {parsedData.filename}</p>
        <p><strong>インポート日時:</strong> {new Date(parsedData.import_date).toLocaleString('ja-JP')}</p>
      {:else if parsedData.isMultiSheet}
        <p><strong>シート数:</strong> {parsedData.sheetNames.length} ({parsedData.sheetNames.join(', ')})</p>
        <p><strong>Sheet1行数:</strong> {parsedData.sheet1Rows}, <strong>Sheet2行数:</strong> {parsedData.sheet2Rows}</p>
      {:else}
        <p><strong>総行数:</strong> {parsedData.totalRows}, <strong>総列数:</strong> {parsedData.totalCols}</p>
        {#if parsedData.sheetName}
          <p><strong>シート名:</strong> {parsedData.sheetName}</p>
        {/if}
      {/if}
      
      <!-- 基本情報表示（Sheet1のデータまたはA5-D7の範囲） -->
      <div class="range-section">
        <h4>{parsedData.isMultiSheet || parsedData.savedData ? '基本情報（Sheet1）' : 'A5-D7の範囲'}</h4>
        {#if rangeA5D7.length > 0}
          <table class="data-table">
            <thead>
              <tr>
                <th>A</th>
                <th>B</th>
                <th>C</th>
                <th>D</th>
              </tr>
            </thead>
            <tbody>
              {#each rangeA5D7 as row, rowIndex}
                <tr>
                  {#each row as cell, colIndex}
                    <td>{cell}</td>
                  {/each}
                </tr>
              {/each}
            </tbody>
          </table>
        {:else}
          <p>データが見つかりませんでした</p>
        {/if}
      </div>

      <!-- 出講日表示 -->
      <div class="attendance-section">
        <h4>{parsedData.isMultiSheet || parsedData.savedData ? '出講日一覧（Sheet2）' : '出講日一覧（B11以降）'}</h4>
        {#if attendanceDates.length > 0}
          <table class="data-table">
            <thead>
              <tr>
                <th>行</th>
                <th>出講日</th>
                {#if parsedData.isMultiSheet || parsedData.savedData}
                  <th>印</th>
                  <th>出勤時刻</th>
                  <th>退勤時刻</th>
                  <th>時間数</th>
                  <th>備考</th>
                {/if}
              </tr>
            </thead>
            <tbody>
              {#each attendanceDates as item}
                <tr>
                  <td>{parsedData.isMultiSheet || parsedData.savedData ? `Sheet2-${item.row || item.row_number}` : `B${item.row}`}</td>
                  <td>{item.date || item.date_text}</td>
                  {#if parsedData.isMultiSheet || parsedData.savedData}
                    <td>{item.attendance || item.attendance_mark}</td>
                    <td>{item.checkIn || item.check_in_time}</td>
                    <td>{item.checkOut || item.check_out_time}</td>
                    <td>{item.hours}</td>
                    <td>{item.notes}</td>
                  {/if}
                </tr>
              {/each}
            </tbody>
          </table>
          <p class="info">合計 {attendanceDates.length} 件の出講日が見つかりました</p>
        {:else}
          <p>出講日が見つかりませんでした</p>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .excel-importer {
    max-width: 1000px;
    margin: 0 auto;
  }

  .card {
    background: white;
    border-radius: 8px;
    padding: 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
  }

  .file-upload-section {
    margin-bottom: 2rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }

  input[type="file"] {
    width: 100%;
    padding: 0.6em;
    font-size: 1em;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-bottom: 0;
  }

  .button-group {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-top: 1rem;
  }

  button {
    border-radius: 8px;
    border: 1px solid transparent;
    padding: 0.6em 1.2em;
    font-size: 1em;
    font-weight: 500;
    font-family: inherit;
    background-color: #007bff;
    color: white;
    cursor: pointer;
    transition: all 0.25s;
  }

  button:hover {
    background-color: #0056b3;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }

  .sample-btn {
    background-color: #6c757d;
  }

  .sample-btn:hover {
    background-color: #5a6268;
  }

  .save-btn {
    background-color: #28a745;
  }

  .save-btn:hover {
    background-color: #218838;
  }

  .saved-data-btn {
    background-color: #17a2b8;
  }

  .saved-data-btn:hover {
    background-color: #138496;
  }

  .load-btn {
    background-color: #007bff;
    padding: 0.25rem 0.5rem;
    font-size: 0.8em;
    margin-right: 0.5rem;
  }

  .load-btn:hover {
    background-color: #0056b3;
  }

  .delete-btn {
    background-color: #dc3545;
    padding: 0.25rem 0.5rem;
    font-size: 0.8em;
  }

  .delete-btn:hover {
    background-color: #c82333;
  }

  .saved-indicator {
    background-color: #d1ecf1;
    color: #0c5460;
    padding: 0.5rem;
    border-radius: 4px;
    margin-bottom: 1rem;
    border-left: 4px solid #bee5eb;
  }

  .file-info {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 4px;
    margin-top: 1rem;
  }

  .file-info h4 {
    margin-top: 0;
    color: #495057;
  }

  .file-info p {
    margin: 0.5rem 0;
    color: #6c757d;
  }

  .range-section, .attendance-section {
    margin: 2rem 0;
  }

  .range-section h4, .attendance-section h4 {
    color: #007bff;
    border-bottom: 2px solid #007bff;
    padding-bottom: 0.5rem;
  }

  .data-table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
    background-color: white;
  }

  .data-table th {
    background-color: #007bff;
    color: white;
    padding: 0.75rem;
    text-align: center;
    font-weight: 600;
    border: 1px solid #007bff;
  }

  .data-table td {
    padding: 0.75rem;
    border: 1px solid #dee2e6;
    text-align: left;
  }

  .data-table tbody tr:nth-child(even) {
    background-color: #f8f9fa;
  }

  .data-table tbody tr:hover {
    background-color: #e3f2fd;
  }

  .error {
    color: #dc3545;
    margin: 0.5rem 0;
  }

  .success {
    color: #28a745;
    margin: 0.5rem 0;
  }

  .info {
    color: #28a745;
    font-weight: 500;
    margin-top: 1rem;
  }

  .file-help {
    display: block;
    margin-top: 0.25rem;
    font-size: 0.875em;
    color: #6c757d;
  }

  @media (max-width: 768px) {
    .button-group {
      flex-direction: column;
    }
    
    .data-table {
      font-size: 0.9em;
    }
    
    .data-table th, .data-table td {
      padding: 0.5rem;
    }
  }
</style>