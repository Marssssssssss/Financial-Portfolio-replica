############################################################################################################
############################################## Graphical Interface #########################################
################################################## Final Work ##############################################
############################################################################################################
# ATTENTION! Remember to install sktime, tkinter, customtkinter, screen info, prophet 

# Import packages 
import pandas as pd
from sktime.forecasting.base import ForecastingHorizon
from sktime.forecasting.fbprophet import Prophet
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
from screeninfo import get_monitors

def conferma_azione():
    input_deposit = deposit.get()
    # Check on the type of the Initial deposit
    # Not a number
    try:
        input_deposit = float(input_deposit)
    except ValueError:
        messagebox.showerror("Errore", "L'importo inserito non è valido")
        # Resetta l'input
        deposit.delete(0, tk.END)
        return
    # Not Positive
    if input_deposit <= 0:
        messagebox.showerror("Errore", "L'importo inserito non è valido")
        # Resetta l'input
        deposit.delete(0, tk.END)
        return

    # Print results on the terminal
    print("Versamento iniziale: ", input_deposit, "€")
    input_horizon = round(horizon.get())
    #
    # Check for the first value
    if input_horizon == 0:
        input_horizon = 1
    print("Durata investimento: ", input_horizon, 'anni')

    # Convert horizon from years to weeks
    input_horizon = input_horizon*52

    # Predict the future price
    monster_df, y_pred, ci = replica(input_horizon)

    # Compute the gross profit
    initial_value = y_pred.Monster_Price.iloc[0]
    final_value = y_pred.Monster_Price.iloc[-1]
    percentage_gain = (final_value - initial_value)/initial_value
    gross_profit = round(input_deposit + input_deposit*percentage_gain,2)
    fourth_row.configure(text=f"Valore investimento: {gross_profit}* €    (+{round(percentage_gain*100,2)}%)")

    # Plot the results
    plt.figure(figsize = (4,3))
    plt.plot(monster_df, label="Prezzo reale", color="Black")
    plt.gca().fill_between(ci.index, (ci.iloc[:, 0]), (ci.iloc[:, 1]), color=(0.64, 0.85, 0.99), alpha=0.5)
    plt.plot(y_pred, label="Previsione")
    plt.plot([monster_df.index[-1], y_pred.index[0]], [monster_df.Monster_Price.iloc[-1], y_pred.Monster_Price.iloc[0]],
             'k--')
    plt.legend()

    # Update the window
    canvas = FigureCanvasTkAgg(plt.gcf(), master=window)
    canvas.draw()
    canvas.get_tk_widget().grid(row=1, column=3, rowspan=5, padx=10, pady=10)

def update_value(event):
    current_value = round(horizon.get())
    if current_value == 1:
        third_row.configure(text=f"Durata: {current_value} Anno")
    else:
        third_row.configure(text=f"Durata: {current_value} Anni")


def replica(horizon):
    # Load the dataset
    df_tot = pd.read_excel("InvestmentReplica.xlsx", sheet_name="Replica")

    # Compute the monster index (price)
    monster_price = df_tot["MXWO"] * 0.80 + df_tot["LEGATRUU"] * 0.15 + df_tot["HFRXGL"] * 0.05

    # We try to forecast to give our client an idea of how the index could evolve in the future and what he/she could earn

    # Create the monster price dataframe
    monster_df = pd.DataFrame({
        'Date': df_tot['Date'],
        'Monster_Price': monster_price
    })
    monster_df.set_index('Date', inplace=True)

    # Set the frequency for data
    monster_df.resample('W').sum()

    # Define forecaster (Prophet)
    forecaster = Prophet()

    # Fit the model
    forecaster.fit(monster_df)

    # Create the forecasting horizon
    last_date = monster_df.index[-1]
    fh = ForecastingHorizon(pd.date_range(str(last_date), periods=horizon, freq="W-TUE"), is_relative=False)

    # Predict using forecaster
    y_pred = forecaster.predict(fh)

    # Confidence interval
    ci = forecaster.predict_interval(fh, coverage=0.5).astype("float")

    return monster_df, y_pred, ci


# Initialize the main window
monitor = get_monitors()[0]
screen_width = monitor.width
screen_height = monitor.height
window_width = int(screen_width * 1.0)
window_height = int(screen_height * 0.8)
window = tk.Tk()
window.geometry(f"{window_width}x{window_height}")

# Initialize the main window
#window = tk.Tk()
#window.geometry("1100x600")
window.title("PREVISIONE INVESTIMENTO")
window.configure(bg="light gray")

# Configure grid layout
for i in range(3):
    window.columnconfigure(i, weight=1)
for i in range(10):
    window.rowconfigure(i, weight=1)


# Title label
title_label = ctk.CTkLabel(master=window, text="PREVISIONE INVESTIMENTO", font=("Helvetica", 24, "bold"))
title_label.grid(row=0, column=3, padx=5, pady=10)

# Initial deposit
first_row = ctk.CTkLabel(master=window, text="Versamento iniziale:", justify="center")
first_row.grid(row=1, column=0, padx=5, pady=5)

deposit = ctk.CTkEntry(window)
deposit.grid(row=1, column=1, padx=5, pady=5)

first_row_right = ctk.CTkLabel(master=window, text="€")
first_row_right.grid(row=1, column=2, padx=5, pady=5, sticky="W")

# Today's date
second_row = ctk.CTkLabel(master=window, text="Data odierna:", justify="center")
second_row.grid(row=2, column=0, padx=5, pady=5)

second_row_right = ctk.CTkLabel(master=window, text="20 / 04 / 2021", justify="center")
second_row_right.grid(row=2, column=1, padx=5, pady=5)


# Investment length
third_row = ctk.CTkLabel(master=window, text="Durata: 1 Anno", justify="center")
third_row.grid(row=3, column=0, padx=5, pady=5)

horizon_style = ttk.Style()
horizon_style.configure("Custom.Horizontal.TScale", background="light gray")

horizon = ttk.Scale(window, from_=1, to=6, orient="horizontal", length=150, command=update_value, style="Custom.Horizontal.TScale")
horizon.grid(row=3, column=1, padx=5, pady=5)

# Create an empty figure
plt.figure(figsize= (4,3))
canvas = FigureCanvasTkAgg(plt.gcf(), master=window)
canvas.draw()
canvas.get_tk_widget().grid(row=1, column=3, rowspan=5, padx=10, pady=10)


# Gross Profit
fourth_row = ctk.CTkLabel(master=window, text="Valore investimento: 0* €    (+0.00%)", justify="center", font=("Helvetica",14,"bold"))
fourth_row.grid(row=6, column=3, padx=5, pady=5)

# Disclaimer
fifth = ctk.CTkLabel(master=window, text="* ATTENZIONE: Le previsioni dell'indice sono elaborate utilizzando tecniche elementari di forecasting,"
                                         " presupponendo che l'attuale trend crescente dell'indice prosegua nel prossimo futuro. \nPertanto, è importante considerare che il guadagno stimato è soggetto a variabili e potrebbe non realizzarsi come previsto. "
                                          "Il guadagno indicato è al lordo delle commissioni. \n" "Invitiamo a valutare attentamente questi fattori"
                                          " prima di prendere decisioni di investimento", font=("Helvetica", 12))
fifth.grid(row=9, column=3, padx=5, pady=5, sticky="S")

# Confirmation button
Confirm_button = ctk.CTkButton(master=window, text="Conferma", command=conferma_azione)
Confirm_button.grid(row=4, column=1, columnspan=1, padx=5, pady=5, sticky="W")

window.mainloop()