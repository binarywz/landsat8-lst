import tkinter as tk
from tkinter import filedialog


def select_file_or_folder():
    selected_path = None

    def select_folder():
        nonlocal selected_path
        folder_path = filedialog.askdirectory()
        if folder_path:
            selected_path = folder_path
            root.withdraw()
            root.destroy()

    def select_file():
        nonlocal selected_path
        file_path = filedialog.askopenfilename()
        if file_path:
            selected_path = file_path
            root.withdraw()
            root.destroy()

    def select_option():
        if option.get() == 1:
            select_file()
        elif option.get() == 2:
            select_folder()

    root = tk.Tk()
    root.withdraw()

    option = tk.IntVar()

    label = tk.Label(root, text="Select an option:")
    label.pack()

    file_button = tk.Radiobutton(root, text="请选择文件", variable=option, value=1, command=select_file)
    file_button.pack()

    folder_button = tk.Radiobutton(root, text="选择文件夹", variable=option, value=2, command=select_folder)
    folder_button.pack()

    root.deiconify()  # 显示窗口
    root.mainloop()

    return selected_path


if __name__ == '__main__':

    path = select_file_or_folder()
    print(path)