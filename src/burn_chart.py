import pandas as pd
import matplotlib.pyplot as plt
import os

metrics_path = os.path.abspath(os.path.join(os.getcwd(), "burn_metrics.csv"))

# Lectura de las métricas en CSV
df = pd.read_csv(metrics_path, parse_dates=['timestamp'])

df = df.sort_values('timestamp')

df['burn_up'] = df['completed'].cumsum()
total_tasks = df['total'].iloc[0] if not df.empty else 0
df['burn_down'] = total_tasks - df['burn_up']

plt.figure()
plt.plot(df['timestamp'], df['burn_up'], marker='o', label='Burn-up (completed)')
plt.plot(df['timestamp'], df['burn_down'], marker='x', label='Burn-down (remaining)')
plt.xlabel('Fecha')
plt.ylabel('Numero de tareas')
plt.title('Tabla Burn-up / Burn-down')
plt.legend()
plt.tight_layout()
plt.show()
