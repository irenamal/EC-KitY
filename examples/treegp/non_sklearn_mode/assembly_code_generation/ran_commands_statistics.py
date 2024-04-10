import os
import subprocess
import xlsxwriter

best_survivors_directory_path = "results"


def unite_results(dest_file):
    workbook = xlsxwriter.Workbook(os.path.join(best_survivors_directory_path, dest_file), {'use_zip64': True})
    sheet = workbook.add_worksheet()
    for ranCommsFile in os.listdir(os.path.join(best_survivors_directory_path, "commands_output")):
        if dest_file.split("_")[2].split(".")[0] != ranCommsFile.split("_")[2]:
            continue
        with open(os.path.join(best_survivors_directory_path, "commands_output", ranCommsFile), "r") as file:
            ranComms = [ranCommsFile.split("_")[0]]
            ranComms = ranComms + file.readlines()
            ranComms.append(ranCommsFile.split("_")[1])
            sheet.write_column(0, int(ranComms[0][3:]), ranComms)
        file.close()
    workbook.close()


def main():
    """ Run one battle against survivor of each generation and save with the scores"""
    nasm_path = "C:\\Users\\irinu\\Desktop\\thesis\\nasm-2.16.01\\nasm.exe"
    engine_path = "results\\corewars8086\\corewars8086-5.1.0-SNAPSHOT-jar-with-dependencies.jar"

    for survivor in os.listdir(best_survivors_directory_path):
        if not survivor.__contains__(".asm"):
            continue
        gen = survivor.split("_")[0]
        score = survivor.split("_")[3]
        with open(os.path.join(best_survivors_directory_path, survivor), "r") as file:
            part1 = []
            part2 = []
            part = part1
            parts = file.readlines()
            for line in parts:
                part.append(line)
                if "@end:\n" == line:
                    part = part2

            part1_path = os.path.join(best_survivors_directory_path, "evolved.asm")
            with open(part1_path, "w+") as f1:
                f1.writelines(part1)
            f1.close()
            proc = subprocess.Popen(
                [nasm_path, "-f bin", part1_path, "-o", os.path.join(best_survivors_directory_path, "corewars8086",
                                                                     "survivors", "evolved1")],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            if "error" in str(stderr):
                print(stderr)
            os.remove(part1_path)

            part2_path = os.path.join(best_survivors_directory_path, "evolved2.asm")
            with open(part2_path, "w+") as f2:
                f2.writelines(part2)
            f2.close()
            proc = subprocess.Popen(
                [nasm_path, "-f bin", part2_path, "-o", os.path.join(best_survivors_directory_path, "corewars8086",
                                                                     "survivors", "evolved2")],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            if "error" in str(stderr):
                print(stderr)
            os.remove(part2_path)

            proc = subprocess.Popen(
                ["java", "-Xmx1500m", "-jar", engine_path,
                 os.path.join(best_survivors_directory_path, "corewars8086", "survivors"),
                 os.path.join(best_survivors_directory_path, "corewars8086", gen + "_scores.csv"),
                 os.path.join(best_survivors_directory_path, "commands_output", gen + "_" + score)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            if "b''" != str(stderr):
                print(stderr)

            os.remove(os.path.join(best_survivors_directory_path, "corewars8086", "survivors", "evolved1"))
            os.remove(os.path.join(best_survivors_directory_path, "corewars8086", "survivors", "evolved2"))

    file1_path = "united_results_evolved1.xlsx"
    file2_path = "united_results_evolved2.xlsx"
    unite_results(file1_path)
    unite_results(file2_path)


if __name__ == '__main__':
    main()
