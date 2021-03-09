import subprocess

cmd = "find -type f -exec sed -i 's/{}/{}/g' {{}} +"

replace_map = {}
replace_map["Возникла ошибка:"] = "An error occurred:"

for k, v in replace_map.items():
    subprocess.run(cmd.format(k, v), shell=True)
