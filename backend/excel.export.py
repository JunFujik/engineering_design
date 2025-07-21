import openpyxl
import requests

def export_excel(filename='attendance.xlsx'):
	"""
	Export attendance data to an Excel file.

	:param data: List of dictionaries containing attendance data.
	:param filename: Name of the output Excel file.
	"""
	# Create a new workbook and select the active worksheet
	workbook = openpyxl.Workbook()
	sheet = workbook.active
	api_url = "http://localhost:3001/api/teacher-salaries"
	response = requests.get(api_url)
	try:
		json_data = response.json()
	except:
		print(response.status_code)
		print(response.text)
	len = len(json_data['id'])
	teacher_name = json_data['teacher_name']
	salary_per_class = json_data['salary_per_class']
	transportation_fee = json_data['transportation_fee']
	sheet.title = teacher_name

	cell_data = [
		['先生名', '1コマあたりの給料', '交通費'],
		[teacher_name, salary_per_class, transportation_fee]
	]
	# Define headers based on keys of the first dictionary in data
	for row_i, row_data in enumerate(cell_data): # 行ごとのデータ取得
		for col_i, data in enumerate(row_data): #行内の列ごとのデータ取得
			col_letter = chr(ord("A")+col_i) # 列アルファベット名の生成(A,B,...とAにcol_iを足して自動生成)
			address = f"{col_letter}{row_i+1}" # セルの位置
			sheet[address] = data # 値格納
	# if data:
	# 	headers = data[0].keys()
	# 	sheet.append(headers)

	# 	# Append each row of data
	# 	for entry in data:
	# 		sheet.append(entry.values())

	# Save the workbook to a file
	workbook.save(filename)

	print(f"Excel file '{filename}' has been created successfully.")

export_excel()
