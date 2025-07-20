<script>
  import { onMount } from 'svelte';
  import { importAPI, userAPI, attendanceAPI, teacherSalaryAPI } from '../lib/api.js';

  let importedDataList = [];
  let users = [];
  let attendanceRecords = [];
  let teacherSalaries = [];
  let selectedTeachers = [];
  let selectedDates = [];
  let loading = false;
  let error = '';
  let success = '';
  let activeTableType = 'teacher'; // 'teacher' or 'date'
  let showSalarySettings = false;
  
  // 表示用データ
  let teacherTable = []; // 先生管理表
  let dateTable = [];    // 日付管理表
  let availableTeachers = []; // 利用可能な先生一覧
  let availableDates = [];    // 利用可能な日付一覧

  // 給料設定用
  let salaryForm = {
    teacher_name: '',
    salary_per_class: 0,
    transportation_fee: 0
  };

  onMount(() => {
    loadData();
  });

  async function loadData() {
    loading = true;
    try {
      // 並行してデータを読み込み
      const [importResponse, userResponse, attendanceResponse, salaryResponse] = await Promise.all([
        importAPI.getAll(),
        userAPI.getAll(),
        attendanceAPI.getAll({}),
        teacherSalaryAPI.getAll()
      ]);
      
      importedDataList = importResponse.data;
      users = userResponse.data;
      attendanceRecords = attendanceResponse.data;
      teacherSalaries = salaryResponse.data;
      
      processAvailableData();
    } catch (err) {
      console.error('データ読み込みエラー:', err);
      error = 'データの読み込みに失敗しました';
    } finally {
      loading = false;
    }
  }

  function processAvailableData() {
    // インポートデータから先生名を抽出
    const importedTeachers = new Set();
    importedDataList.forEach(data => {
      if (data.basic_info?.name) {
        importedTeachers.add(data.basic_info.name);
      }
    });

    // ユーザーテーブルからユーザー名を抽出
    const registeredUsers = new Set();
    users.forEach(user => {
      registeredUsers.add(user.name);
    });

    // 利用可能な先生一覧（インポートデータ + 登録ユーザー）
    availableTeachers = [...new Set([...importedTeachers, ...registeredUsers])].sort();

    // インポートデータから日付を抽出し、2025-04-08形式に統一
    const importedDates = new Set();
    importedDataList.forEach(data => {
      if (data.attendance_dates) {
        data.attendance_dates.forEach(item => {
          if (item.date_text && item.date_text.trim() !== '') {
            const normalizedDate = normalizeDateFormat(item.date_text);
            if (normalizedDate) {
              importedDates.add(normalizedDate);
            }
          }
        });
      }
    });

    // 勤怠記録から日付を抽出（既に2025-04-08形式）
    const attendanceDates = new Set();
    attendanceRecords.forEach(record => {
      if (record.date) {
        attendanceDates.add(record.date);
      }
    });

    // 利用可能な日付一覧（インポートデータ + 勤怠記録）
    availableDates = [...new Set([...importedDates, ...attendanceDates])].sort();
  }

  // 日付形式を2025-04-08形式に正規化
  function normalizeDateFormat(dateStr) {
    if (!dateStr || dateStr.trim() === '') return null;
    
    // 既に2025-04-08形式の場合
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
      return dateStr;
    }
    
    // YYYY/MM/DD形式から変換
    if (/^\d{4}\/\d{1,2}\/\d{1,2}$/.test(dateStr)) {
      const parts = dateStr.split('/');
      const year = parts[0];
      const month = parts[1].padStart(2, '0');
      const day = parts[2].padStart(2, '0');
      return `${year}-${month}-${day}`;
    }
    
    // MM/DD形式（現在年として処理）
    if (/^\d{1,2}\/\d{1,2}$/.test(dateStr)) {
      const parts = dateStr.split('/');
      const currentYear = new Date().getFullYear();
      const month = parts[0].padStart(2, '0');
      const day = parts[1].padStart(2, '0');
      return `${currentYear}-${month}-${day}`;
    }
    
    // YYYY年MM月DD日形式から変換
    if (/^\d{4}年\d{1,2}月\d{1,2}日$/.test(dateStr)) {
      const match = dateStr.match(/^(\d{4})年(\d{1,2})月(\d{1,2})日$/);
      if (match) {
        const year = match[1];
        const month = match[2].padStart(2, '0');
        const day = match[3].padStart(2, '0');
        return `${year}-${month}-${day}`;
      }
    }
    
    // MM月DD日形式（現在年として処理）
    if (/^\d{1,2}月\d{1,2}日$/.test(dateStr)) {
      const match = dateStr.match(/^(\d{1,2})月(\d{1,2})日$/);
      if (match) {
        const currentYear = new Date().getFullYear();
        const month = match[1].padStart(2, '0');
        const day = match[2].padStart(2, '0');
        return `${currentYear}-${month}-${day}`;
      }
    }
    
    return null; // 変換できない場合
  }

  function generateTables() {
    if (selectedTeachers.length === 0 && selectedDates.length === 0) {
      teacherTable = [];
      dateTable = [];
      return;
    }

    const teachers = selectedTeachers.length > 0 ? selectedTeachers : availableTeachers;
    const dates = selectedDates.length > 0 ? selectedDates : availableDates;

    // 出勤データをマップ化（授業名を配列で保存）
    const attendanceMap = {};

    // インポートデータから出勤情報を収集
    importedDataList.forEach(data => {
      const teacherName = data.basic_info?.name;
      const subjectName = data.basic_info?.subject || '授業科目未設定';
      
      if (teacherName && teachers.includes(teacherName)) {
        data.attendance_dates?.forEach(item => {
          const normalizedDate = normalizeDateFormat(item.date_text);
          if (normalizedDate && dates.includes(normalizedDate)) {
            const key = `${teacherName}_${normalizedDate}`;
            if (!attendanceMap[key]) {
              attendanceMap[key] = [];
            }
            // 出勤マークがある場合のみ授業名を追加
            if (item.attendance_mark && item.attendance_mark.trim() !== '' && item.attendance_mark !== '-') {
              // 既に同じ授業が追加されていない場合のみ追加
              if (!attendanceMap[key].includes(subjectName)) {
                attendanceMap[key].push(subjectName);
              }
            }
          }
        });
      }
    });

    // 勤怠記録から出勤情報を収集（先生名が一致する場合）
    attendanceRecords.forEach(record => {
      const user = users.find(u => u.id === record.user_id);
      if (user && teachers.includes(user.name) && dates.includes(record.date)) {
        const key = `${user.name}_${record.date}`;
        if (!attendanceMap[key]) {
          attendanceMap[key] = [];
        }
        // 出勤時刻または退勤時刻がある場合は授業ありとみなす
        if (record.check_in || record.check_out) {
          // インポートデータから該当する先生の授業科目を取得
          const teacherImportData = importedDataList.find(data => 
            data.basic_info?.name === user.name
          );
          
          if (teacherImportData && teacherImportData.basic_info?.subject) {
            const subjectName = teacherImportData.basic_info.subject;
            if (!attendanceMap[key].includes(subjectName)) {
              attendanceMap[key].push(subjectName);
            }
          } else {
            // インポートデータがない場合は「勤怠打刻」として記録
            if (!attendanceMap[key].includes('勤怠打刻')) {
              attendanceMap[key].push('勤怠打刻');
            }
          }
        }
      }
    });

    // 先生管理表を作成（先生名 × 日付）
    teacherTable = teachers.map(teacher => ({
      teacher,
      attendances: dates.map(date => ({
        date,
        subjects: attendanceMap[`${teacher}_${date}`] || []
      }))
    }));

    // 日付管理表を作成（日付 × 先生名）
    dateTable = dates.map(date => ({
      date,
      attendances: teachers.map(teacher => ({
        teacher,
        subjects: attendanceMap[`${teacher}_${date}`] || []
      }))
    }));
  }

  function hasAttendance(subjects) {
    return subjects && subjects.length > 0;
  }

  function formatSubjects(subjects) {
    if (!subjects || subjects.length === 0) {
      return '';
    }
    return subjects.join('\n');
  }

  function addTeacher(teacherName) {
    if (teacherName && !selectedTeachers.includes(teacherName)) {
      selectedTeachers = [...selectedTeachers, teacherName];
      generateTables();
    }
  }

  function removeTeacher(teacherName) {
    selectedTeachers = selectedTeachers.filter(t => t !== teacherName);
    generateTables();
  }

  function addDate(date) {
    if (date && !selectedDates.includes(date)) {
      selectedDates = [...selectedDates, date].sort();
      generateTables();
    }
  }

  function removeDate(date) {
    selectedDates = selectedDates.filter(d => d !== date);
    generateTables();
  }

  function selectAllTeachers() {
    selectedTeachers = [...availableTeachers];
    generateTables();
  }

  function clearAllTeachers() {
    selectedTeachers = [];
    generateTables();
  }

  function selectAllDates() {
    selectedDates = [...availableDates];
    generateTables();
  }

  function clearAllDates() {
    selectedDates = [];
    generateTables();
  }

  async function saveSalarySetting() {
    if (!salaryForm.teacher_name) {
      error = '先生名を選択してください';
      return;
    }

    try {
      await teacherSalaryAPI.createOrUpdate(salaryForm);
      success = '給料設定を保存しました';
      await loadTeacherSalaries();
      resetSalaryForm();
    } catch (err) {
      console.error('給料設定保存エラー:', err);
      error = '給料設定の保存に失敗しました';
    }
  }

  async function loadTeacherSalaries() {
    try {
      const response = await teacherSalaryAPI.getAll();
      teacherSalaries = response.data;
    } catch (err) {
      console.error('給料設定読み込みエラー:', err);
    }
  }

  async function deleteSalarySetting(salaryId) {
    if (!confirm('この給料設定を削除しますか？')) return;
    
    try {
      await teacherSalaryAPI.delete(salaryId);
      success = '給料設定を削除しました';
      await loadTeacherSalaries();
    } catch (err) {
      console.error('給料設定削除エラー:', err);
      error = '給料設定の削除に失敗しました';
    }
  }

  function resetSalaryForm() {
    salaryForm = {
      teacher_name: '',
      salary_per_class: 0,
      transportation_fee: 0
    };
  }

  function loadExistingSalary(teacherName) {
    const existing = teacherSalaries.find(s => s.teacher_name === teacherName);
    if (existing) {
      salaryForm = {
        teacher_name: existing.teacher_name,
        salary_per_class: existing.salary_per_class,
        transportation_fee: existing.transportation_fee
      };
    } else {
      salaryForm = {
        teacher_name: teacherName,
        salary_per_class: 0,
        transportation_fee: 0
      };
    }
  }

  // 初期データ読み込み完了後にテーブルを生成
  $: if (!loading && availableTeachers.length > 0 && availableDates.length > 0) {
    generateTables();
  }
</script>

<div class="attendance-viewer">
  <div class="card">
    <h2>出勤簿表示・給料設定</h2>
    
    {#if error}
      <p class="error">{error}</p>
    {/if}

    {#if success}
      <p class="success">{success}</p>
    {/if}

    {#if loading}
      <p>データを読み込み中...</p>
    {:else}
      <!-- メニュー選択 -->
      <div class="menu-selector">
        <button 
          class="menu-btn" 
          class:active={!showSalarySettings}
          on:click={() => showSalarySettings = false}
        >
          出勤簿表示
        </button>
        <button 
          class="menu-btn" 
          class:active={showSalarySettings}
          on:click={() => showSalarySettings = true}
        >
          給料設定
        </button>
      </div>

      {#if !showSalarySettings}
        <!-- 出勤簿表示 -->
        <div class="filter-section">
          <h3>表示設定</h3>
          
          <!-- 先生選択 -->
          <div class="selection-group">
            <h4>先生選択</h4>
            <div class="selection-controls">
              <select on:change={(e) => { if(e.target.value) addTeacher(e.target.value); e.target.value = ''; }}>
                <option value="">先生を追加...</option>
                {#each availableTeachers.filter(t => !selectedTeachers.includes(t)) as teacher}
                  <option value={teacher}>{teacher}</option>
                {/each}
              </select>
              <button on:click={selectAllTeachers} class="select-all-btn">全選択</button>
              <button on:click={clearAllTeachers} class="clear-btn">クリア</button>
            </div>
            <div class="selected-items">
              {#each selectedTeachers as teacher}
                <span class="selected-item">
                  {teacher}
                  <button on:click={() => removeTeacher(teacher)} class="remove-btn">×</button>
                </span>
              {/each}
            </div>
          </div>

          <!-- 日付選択 -->
          <div class="selection-group">
            <h4>日付選択</h4>
            <div class="selection-controls">
              <select on:change={(e) => { if(e.target.value) addDate(e.target.value); e.target.value = ''; }}>
                <option value="">日付を追加...</option>
                {#each availableDates.filter(d => !selectedDates.includes(d)) as date}
                  <option value={date}>{date}</option>
                {/each}
              </select>
              <button on:click={selectAllDates} class="select-all-btn">全選択</button>
              <button on:click={clearAllDates} class="clear-btn">クリア</button>
            </div>
            <div class="selected-items">
              {#each selectedDates as date}
                <span class="selected-item">
                  {date}
                  <button on:click={() => removeDate(date)} class="remove-btn">×</button>
                </span>
              {/each}
            </div>
          </div>
        </div>

        <!-- 表タイプ選択 -->
        {#if (selectedTeachers.length > 0 || selectedDates.length > 0)}
          <div class="table-type-selector">
            <button 
              class="table-type-btn" 
              class:active={activeTableType === 'teacher'}
              on:click={() => activeTableType = 'teacher'}
            >
              先生管理表
            </button>
            <button 
              class="table-type-btn" 
              class:active={activeTableType === 'date'}
              on:click={() => activeTableType = 'date'}
            >
              日付管理表
            </button>
          </div>

          <div class="data-info">
            <h4>表示情報</h4>
            <p><strong>選択先生数:</strong> {selectedTeachers.length > 0 ? selectedTeachers.length : availableTeachers.length}人</p>
            <p><strong>選択日付数:</strong> {selectedDates.length > 0 ? selectedDates.length : availableDates.length}日</p>
            <p><strong>データソース:</strong> インポートデータ（授業科目） + 勤怠記録</p>
            <p><strong>表示内容:</strong> 出勤した日の授業科目名を改行区切りで表示</p>
          </div>

          <!-- 先生管理表 -->
          {#if activeTableType === 'teacher'}
            <div class="table-section">
              <h3>先生管理表（先生 × 日付）</h3>
              <div class="table-container">
                <table class="attendance-table">
                  <thead>
                    <tr>
                      <th class="teacher-header">先生の名前</th>
                      {#each (selectedDates.length > 0 ? selectedDates : availableDates) as date}
                        <th class="date-header">{date}</th>
                      {/each}
                    </tr>
                  </thead>
                  <tbody>
                    {#each teacherTable as row}
                      <tr>
                        <td class="teacher-name">{row.teacher}</td>
                        {#each row.attendances as attendance}
                          <td class="attendance-cell" class:has-subjects={hasAttendance(attendance.subjects)}>
                            <div class="subjects-list">
                              {#each attendance.subjects as subject}
                                <div class="subject-item">{subject}</div>
                              {/each}
                            </div>
                          </td>
                        {/each}
                      </tr>
                    {/each}
                  </tbody>
                </table>
              </div>
            </div>
          {/if}

          <!-- 日付管理表 -->
          {#if activeTableType === 'date'}
            <div class="table-section">
              <h3>日付管理表（日付 × 先生）</h3>
              <div class="table-container">
                <table class="attendance-table">
                  <thead>
                    <tr>
                      <th class="date-header-vertical">1ヶ月もしくは1年単位での日付</th>
                      {#each (selectedTeachers.length > 0 ? selectedTeachers : availableTeachers) as teacher}
                        <th class="teacher-header">{teacher}</th>
                      {/each}
                    </tr>
                  </thead>
                  <tbody>
                    {#each dateTable as row}
                      <tr>
                        <td class="date-name">{row.date}</td>
                        {#each row.attendances as attendance}
                          <td class="attendance-cell" class:has-subjects={hasAttendance(attendance.subjects)}>
                            <div class="subjects-list">
                              {#each attendance.subjects as subject}
                                <div class="subject-item">{subject}</div>
                              {/each}
                            </div>
                          </td>
                        {/each}
                      </tr>
                    {/each}
                  </tbody>
                </table>
              </div>
            </div>
          {/if}
        {:else}
          <div class="no-selection">
            <p>先生または日付を選択して表を表示してください。</p>
          </div>
        {/if}
      {:else}
        <!-- 給料設定画面 -->
        <div class="salary-settings">
          <h3>給料設定</h3>
          
          <div class="salary-form">
            <h4>新規設定・更新</h4>
            <div class="form-group">
              <label for="teacher-select">先生選択</label>
              <select 
                id="teacher-select" 
                bind:value={salaryForm.teacher_name}
                on:change={() => loadExistingSalary(salaryForm.teacher_name)}
              >
                <option value="">先生を選択してください</option>
                {#each availableTeachers as teacher}
                  <option value={teacher}>{teacher}</option>
                {/each}
              </select>
            </div>
            
            <div class="form-group">
              <label for="salary-per-class">1コマあたりの給料（円）</label>
              <input 
                id="salary-per-class"
                type="number" 
                bind:value={salaryForm.salary_per_class}
                min="0"
                placeholder="5000"
              />
            </div>
            
            <div class="form-group">
              <label for="transportation-fee">交通費（円）</label>
              <input 
                id="transportation-fee"
                type="number" 
                bind:value={salaryForm.transportation_fee}
                min="0"
                placeholder="500"
              />
            </div>
            
            <div class="form-actions">
              <button on:click={saveSalarySetting} class="save-btn">保存</button>
              <button on:click={resetSalaryForm} class="reset-btn">リセット</button>
            </div>
          </div>

          <!-- 既存の給料設定一覧 -->
          <div class="salary-list">
            <h4>現在の給料設定</h4>
            {#if teacherSalaries.length > 0}
              <table class="salary-table">
                <thead>
                  <tr>
                    <th>先生名</th>
                    <th>1コマあたりの給料</th>
                    <th>交通費</th>
                    <th>更新日</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {#each teacherSalaries as salary}
                    <tr>
                      <td>{salary.teacher_name}</td>
                      <td>{salary.salary_per_class.toLocaleString()}円</td>
                      <td>{salary.transportation_fee.toLocaleString()}円</td>
                      <td>{new Date(salary.updated_at).toLocaleDateString('ja-JP')}</td>
                      <td>
                        <button on:click={() => loadExistingSalary(salary.teacher_name)} class="edit-btn">編集</button>
                        <button on:click={() => deleteSalarySetting(salary.id)} class="delete-btn">削除</button>
                      </td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            {:else}
              <p>給料設定がありません</p>
            {/if}
          </div>
        </div>
      {/if}
    {/if}
  </div>
</div>

<style>
  .attendance-viewer {
    max-width: 100%;
    margin: 0 auto;
  }

  .card {
    background: white;
    border-radius: 8px;
    padding: 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
  }

  .menu-selector {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
    border-bottom: 2px solid #ddd;
  }

  .menu-btn {
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    color: #666;
    padding: 0.75rem 1.5rem;
    margin-bottom: -2px;
    cursor: pointer;
    font-size: 1.1em;
    transition: all 0.2s;
  }

  .menu-btn.active {
    color: #007bff;
    border-bottom-color: #007bff;
    font-weight: 600;
  }

  .menu-btn:hover {
    color: #007bff;
  }

  .filter-section {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    margin-bottom: 2rem;
    border: 1px solid #dee2e6;
  }

  .filter-section h3 {
    margin-top: 0;
    color: #495057;
    border-bottom: 2px solid #007bff;
    padding-bottom: 0.5rem;
  }

  .selection-group {
    margin-bottom: 1.5rem;
  }

  .selection-group h4 {
    margin-bottom: 0.5rem;
    color: #6c757d;
  }

  .selection-controls {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
  }

  .selection-controls select {
    flex: 1;
    min-width: 200px;
    padding: 0.5rem;
    border: 1px solid #ced4da;
    border-radius: 4px;
  }

  .select-all-btn, .clear-btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9em;
  }

  .select-all-btn {
    background-color: #28a745;
    color: white;
  }

  .select-all-btn:hover {
    background-color: #218838;
  }

  .clear-btn {
    background-color: #6c757d;
    color: white;
  }

  .clear-btn:hover {
    background-color: #5a6268;
  }

  .selected-items {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .selected-item {
    background-color: #007bff;
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.9em;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .remove-btn {
    background: none;
    border: none;
    color: white;
    cursor: pointer;
    font-weight: bold;
    padding: 0;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .remove-btn:hover {
    background-color: rgba(255, 255, 255, 0.2);
  }

  .table-type-selector {
    display: flex;
    gap: 1rem;
    margin: 1.5rem 0;
    border-bottom: 2px solid #ddd;
  }

  .table-type-btn {
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    color: #666;
    padding: 0.5rem 1rem;
    margin-bottom: -2px;
    cursor: pointer;
    font-size: 1em;
    transition: all 0.2s;
  }

  .table-type-btn.active {
    color: #007bff;
    border-bottom-color: #007bff;
    font-weight: 600;
  }

  .table-type-btn:hover {
    color: #007bff;
  }

  .data-info {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 4px;
    margin: 1rem 0 2rem 0;
    border-left: 4px solid #007bff;
  }

  .data-info h4 {
    margin-top: 0;
    margin-bottom: 0.5rem;
    color: #495057;
  }

  .data-info p {
    margin: 0.25rem 0;
    color: #6c757d;
  }

  .no-selection {
    text-align: center;
    padding: 3rem;
    color: #6c757d;
    background-color: #f8f9fa;
    border-radius: 8px;
    border: 2px dashed #dee2e6;
  }

  .table-section {
    margin: 2rem 0;
  }

  .table-section h3 {
    color: #007bff;
    border-bottom: 2px solid #007bff;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
  }

  .table-container {
    overflow-x: auto;
    margin: 1rem 0;
    border: 1px solid #dee2e6;
    border-radius: 4px;
  }

  .attendance-table {
    width: 100%;
    border-collapse: collapse;
    background-color: white;
    min-width: 600px;
  }

  .attendance-table th {
    background-color: #007bff;
    color: white;
    padding: 0.75rem;
    text-align: center;
    font-weight: 600;
    border: 1px solid #007bff;
    font-size: 0.9em;
  }

  .attendance-table td {
    padding: 0.75rem;
    border: 1px solid #dee2e6;
    text-align: center;
    font-size: 0.9em;
    vertical-align: top;
  }

  .teacher-header, .teacher-name {
    background-color: #e3f2fd !important;
    font-weight: 500;
    min-width: 120px;
  }

  .date-header, .date-name {
    background-color: #f3e5f5 !important;
    font-weight: 500;
    min-width: 100px;
    font-size: 0.8em;
  }

  .date-header-vertical {
    background-color: #f3e5f5 !important;
    font-weight: 500;
    min-width: 150px;
    writing-mode: horizontal-tb;
  }

  .attendance-cell {
    background-color: #f8f9fa;
    min-width: 120px;
    padding: 0.5rem;
  }

  .attendance-cell.has-subjects {
    background-color: #d4edda;
  }

  .subjects-list {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    text-align: left;
  }

  .subject-item {
    background-color: rgba(255, 255, 255, 0.9);
    padding: 0.3rem 0.6rem;
    border-radius: 4px;
    font-size: 0.85em;
    border-left: 3px solid #28a745;
    word-break: break-word;
    margin-bottom: 0.1rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    font-weight: 500;
    color: #155724;
  }

  .attendance-table tbody tr:hover {
    background-color: rgba(0, 123, 255, 0.1);
  }

  /* 給料設定のスタイル */
  .salary-settings {
    max-width: 800px;
  }

  .salary-form {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    margin-bottom: 2rem;
    border: 1px solid #dee2e6;
  }

  .salary-form h4 {
    margin-top: 0;
    color: #495057;
    border-bottom: 2px solid #17a2b8;
    padding-bottom: 0.5rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #495057;
  }

  .form-group input, .form-group select {
    width: 100%;
    padding: 0.6rem;
    border: 1px solid #ced4da;
    border-radius: 4px;
    font-size: 1em;
  }

  .form-actions {
    display: flex;
    gap: 1rem;
    margin-top: 1.5rem;
  }

  .save-btn {
    background-color: #28a745;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
  }

  .save-btn:hover {
    background-color: #218838;
  }

  .reset-btn {
    background-color: #6c757d;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
  }

  .reset-btn:hover {
    background-color: #5a6268;
  }

  .salary-list {
    background-color: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1.5rem;
  }

  .salary-list h4 {
    margin-top: 0;
    color: #495057;
    border-bottom: 2px solid #17a2b8;
    padding-bottom: 0.5rem;
  }

  .salary-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
  }

  .salary-table th {
    background-color: #17a2b8;
    color: white;
    padding: 0.75rem;
    text-align: left;
    font-weight: 600;
    border: 1px solid #17a2b8;
  }

  .salary-table td {
    padding: 0.75rem;
    border: 1px solid #dee2e6;
  }

  .salary-table tbody tr:nth-child(even) {
    background-color: #f8f9fa;
  }

  .salary-table tbody tr:hover {
    background-color: #e3f2fd;
  }

  .edit-btn {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 0.25rem 0.5rem;
    border-radius: 3px;
    cursor: pointer;
    font-size: 0.8em;
    margin-right: 0.5rem;
  }

  .edit-btn:hover {
    background-color: #0056b3;
  }

  .delete-btn {
    background-color: #dc3545;
    color: white;
    border: none;
    padding: 0.25rem 0.5rem;
    border-radius: 3px;
    cursor: pointer;
    font-size: 0.8em;
  }

  .delete-btn:hover {
    background-color: #c82333;
  }

  .error {
    color: #dc3545;
    margin: 0.5rem 0;
    padding: 0.75rem;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 4px;
  }

  .success {
    color: #155724;
    margin: 0.5rem 0;
    padding: 0.75rem;
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 4px;
  }

  @media (max-width: 768px) {
    .card {
      padding: 1rem;
    }
    
    .filter-section, .salary-form {
      padding: 1rem;
    }
    
    .selection-controls, .form-actions {
      flex-direction: column;
    }
    
    .attendance-table, .salary-table {
      font-size: 0.8em;
    }
    
    .attendance-table th, 
    .attendance-table td,
    .salary-table th,
    .salary-table td {
      padding: 0.5rem;
    }
    
    .table-type-selector, .menu-selector {
      flex-direction: column;
      gap: 0.5rem;
    }

    .subjects-list {
      font-size: 0.8em;
    }

    .subject-item {
      font-size: 0.7em;
    }
  }
</style>