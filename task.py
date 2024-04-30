import tkinter as tk
from tkinter import ttk, messagebox
import psutil
from collections import deque

class TaskManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Administrador de Tareas")
        
        self.process_mode = tk.StringVar()
        self.process_mode.set("FIFO")
        
        self.process_stack = deque()
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.create_processes_tab()
        self.create_performance_tab()
        self.create_startup_tab()
        
        self.root.after(1000, self.update_processes)
        self.root.after(1000, self.update_performance)
        self.root.mainloop()
    
    def create_processes_tab(self):
        processes_frame = tk.Frame(self.notebook)
        self.notebook.add(processes_frame, text="Procesos")
        
        self.processes_list = tk.Listbox(processes_frame, selectmode=tk.SINGLE)
        self.processes_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(processes_frame, orient="vertical", command=self.processes_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.processes_list.config(yscrollcommand=scrollbar.set)
        
        button_frame = tk.Frame(processes_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        kill_button = tk.Button(button_frame, text="Finalizar tarea", command=self.kill_process)
        kill_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        refresh_button = tk.Button(button_frame, text="Actualizar lista", command=self.update_processes)
        refresh_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        fifo_button = tk.Radiobutton(button_frame, text="FIFO", variable=self.process_mode, value="FIFO")
        fifo_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        lifo_button = tk.Radiobutton(button_frame, text="LIFO", variable=self.process_mode, value="LIFO")
        lifo_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.selected_processes_list = tk.Listbox(processes_frame, selectmode=tk.MULTIPLE)
        self.selected_processes_list.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        add_button = tk.Button(button_frame, text="Añadir a lista", command=self.add_to_selected)
        add_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        execute_button = tk.Button(button_frame, text="Ejecutar", command=self.execute_processes)
        execute_button.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def create_performance_tab(self):
        performance_frame = tk.Frame(self.notebook)
        self.notebook.add(performance_frame, text="Rendimiento")
        
        self.performance_text = tk.Text(performance_frame, wrap=tk.WORD)
        self.performance_text.pack(fill=tk.BOTH, expand=True)
    
    def create_startup_tab(self):
        startup_frame = tk.Frame(self.notebook)
        self.notebook.add(startup_frame, text="Inicio")
        
        self.startup_text = tk.Text(startup_frame, wrap=tk.WORD)
        self.startup_text.pack(fill=tk.BOTH, expand=True)
        
        refresh_button = tk.Button(startup_frame, text="Actualizar lista", command=self.update_startup)
        refresh_button.pack(pady=5)
        
    def update_processes(self):
        self.processes_list.delete(0, tk.END)
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name'])
                self.processes_list.insert(tk.END, f"{pinfo['pid']}: {pinfo['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    
    def kill_process(self):
        selected_index = self.processes_list.curselection()
        if selected_index:
            selected_process = self.processes_list.get(selected_index[0])
            self.selected_processes_list.insert(tk.END, selected_process)
        else:
            messagebox.showwarning("No se ha seleccionado ninguna tarea", "Por favor, seleccione una tarea de la lista.")
    
    def add_to_selected(self):
        selected_index = self.processes_list.curselection()
        if selected_index:
            selected_process = self.processes_list.get(selected_index[0])
            self.selected_processes_list.insert(tk.END, selected_process)
        else:
            messagebox.showwarning("No se ha seleccionado ninguna tarea", "Por favor, seleccione una tarea de la lista.")
    
    def execute_processes(self):
        process_ids = [item.split(':')[0] for item in self.selected_processes_list.get(0, tk.END)]
        if self.process_mode.get() == "FIFO":
            while self.selected_processes_list.size() > 0:
                messagebox.showinfo("Proceso Ejecutado", f"El proceso {self.selected_processes_list.get(0)} ha sido ejecutado.")
                self.selected_processes_list.delete(0)
        else:
            while self.selected_processes_list.size() > 0:
                messagebox.showinfo("Proceso Ejecutado", f"El proceso {self.selected_processes_list.get(tk.END)} ha sido ejecutado.")
                self.selected_processes_list.delete(tk.END)
    
    def update_performance(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        network_usage = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        
        self.performance_text.delete(1.0, tk.END)
        self.performance_text.insert(tk.END, f"Uso de CPU: {cpu_usage:.2f}%\n")
        self.performance_text.insert(tk.END, f"Uso de Memoria: {memory_usage:.2f}%\n")
        self.performance_text.insert(tk.END, f"Uso de Disco: {disk_usage:.2f}%\n")
        self.performance_text.insert(tk.END, f"Uso de Red: {network_usage} bytes\n")
        
        self.root.after(1000, self.update_performance)
    
    def update_startup(self):
        startup_programs = []
        with os.popen('wmic startup get Caption') as f:
            for line in f.readlines():
                startup_programs.append(line.strip())
        
        self.startup_text.delete(1.0, tk.END)
        for program in startup_programs:
            self.startup_text.insert(tk.END, f"{program}\n")

if __name__ == "__main__":
    TaskManager()
