import flet as ft
import math
from flet import ControlEvent


# --- Configuration ---
APP_TITLE = "Zinsrechner (Flet)"

# --- NEUE Reine Python-Lösung für root_scalar (Bisektion) ---

def bisection_solver(func, a, b, tol=1e-5, max_iter=100):
    """Löst func(x) = 0 für x im Intervall [a, b] mit der Bisektionsmethode."""
    if func(a) * func(b) >= 0:
        return None  # Keine oder gerade Anzahl von Wurzeln
    
    for _ in range(max_iter):
        c = (a + b) / 2
        if abs(func(c)) < tol or (b - a) / 2 < tol:
            return c
        if func(c) * func(a) < 0:
            b = c
        else:
            a = c
            
    return None # Konvergiert nicht innerhalb der Iterationen


# ------------------ Calculation Functions ------------------
# (Dieser Block bleibt identisch, da er die Logik enthält)

def calculate_final_capital(starting_capital, interest_rate, years, monthly_contribution):
    """
    Calculate the final capital from given parameters. 
    """
    yearly_rate = interest_rate / 100 
    months = int(years * 12)
    final_capital = starting_capital * (1 + yearly_rate) ** years

    j=(1+yearly_rate)**(1/12)

    for m in range(1, months + 1):
        final_capital += monthly_contribution * j ** m

    return final_capital


def calculate_starting_capital(final_capital, interest_rate, years, monthly_contribution):
    """
    Calculate the required starting capital to reach a desired final capital.
    """
    yearly_rate = interest_rate / 100
    months = int(years * 12)
    j = (1 + yearly_rate) ** (1 / 12)

    contribution_sum = 0
    for m in range(1, months + 1):
        contribution_sum += monthly_contribution * j ** m

    starting_capital = (final_capital - contribution_sum) / ((1 + yearly_rate) ** years)

    return starting_capital

def objective_interest_rate(yearly_rate, starting_capital, years, final_capital, monthly_contribution):
    """
    Objective function for SciPy's root_scalar to find the interest rate.
    """
    yearly_factor = 1 + yearly_rate
    months = int(years * 12)
    
    calculated_final_capital = starting_capital * yearly_factor ** years
    
    j = yearly_factor ** (1 / 12)

    for m in range(1, months + 1):
        calculated_final_capital += monthly_contribution * j ** m
        
    return calculated_final_capital - final_capital


def calculate_interest_rate(starting_capital, years, final_capital, monthly_contribution):
    """
    Calculate the required interest rate using the bisection_solver.
    """
    min_final_capital = starting_capital + monthly_contribution * years * 12
    if final_capital < min_final_capital:
        return 0.0 # Zinssatz kann 0% sein, wenn es durch Beiträge erreicht wird.

    # Das Bracket (Suchintervall) von [0.0, 1.0] (0% bis 100%) verwenden
    result_rate = bisection_solver(
        objective_interest_rate, 
        a=0.0, 
        b=1.0, 
        args=(starting_capital, years, final_capital, monthly_contribution) # args muss entfernt werden, da bisection_solver es nicht direkt nimmt
    )

    # Wir müssen objective_interest_rate für bisection_solver anpassen (Closure)
    def func_rate(rate):
        return objective_interest_rate(rate, starting_capital, years, final_capital, monthly_contribution)

    result_rate = bisection_solver(func_rate, a=0.0, b=1.0)

    if result_rate is not None:
        return result_rate * 100
    else:
        return None

def objective_years(years, starting_capital, yearly_rate, final_capital, monthly_contribution):
    """
    Zielfunktion für SciPy's root_scalar zur Bestimmung der Dauer (Jahre).
    """
    
    yearly_factor = 1 + yearly_rate
    calculated_final_capital = starting_capital * yearly_factor ** years
    
    contribution_sum = 0
    
    if monthly_contribution > 0 and years > 0:
        N = years * 12
        
        if yearly_rate == 0:
            contribution_sum = monthly_contribution * N
        else:
            j = yearly_factor ** (1 / 12)
            contribution_sum = monthly_contribution * j * (j**N - 1) / (j - 1)
            
        calculated_final_capital += contribution_sum
        
    return calculated_final_capital - final_capital


def calculate_years(starting_capital, interest_rate, final_capital, monthly_contribution):
    """
    Berechnet die erforderliche Dauer (Jahre) mithilfe der bisection_solver-Funktion.
    """
    yearly_rate = interest_rate / 100
    
    if final_capital <= starting_capital:
        return 0.0

    # ... (Ihre einfachen Fallüberprüfungen für 0% Zins oder 0 Monatsbeitrag bleiben) ...
    
    # Ermitteln des maximalen Suchbereichs (Bracket)
    max_test_years = 200.0
    max_years = None
    
    current_years = 1.0
    while current_years <= max_test_years:
        if objective_years(current_years, starting_capital, yearly_rate, final_capital, monthly_contribution) > 0:
            max_years = current_years
            break
        current_years *= 2
    else:
        return None

    # Wir müssen objective_years für bisection_solver anpassen (Closure)
    def func_years(years):
        return objective_years(years, starting_capital, yearly_rate, final_capital, monthly_contribution)

    result_years = bisection_solver(func_years, a=0.0, b=max_years)


    if result_years is not None:
        return result_years
    else:
        return None

def calculate_monthly_contribution(starting_capital, interest_rate, years, final_capital):
    """
    Calculate the required monthly contribution to reach a desired final capital.
    """
    yearly_rate = interest_rate / 100
    months = int(years * 12)

    starting_capital_future_value = starting_capital * (1 + yearly_rate) ** years
    target_contributions = final_capital - starting_capital_future_value

    if target_contributions < 0:
        return 0.0

    if yearly_rate == 0.0:
        if months > 0:
            return target_contributions / months
        else:
            return 0.0 

    j = (1 + yearly_rate) ** (1 / 12)
    contribution_factor = j * (j ** months - 1) / (j - 1)
    
    monthly_contribution = target_contributions / contribution_factor

    return monthly_contribution


# ------------------ Flet GUI Logic (Modern/Stable) ------------------

def main(page: ft.Page):
    page.title = APP_TITLE
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    class Colors:
        BLUE_700 = "#1976D2"  # Standardwert für das Result Label
        GREEN_700 = "#388E3C" # Standardwert für den Button
        WHITE = "#FFFFFF"     # Standardwert für den Button-Text
    
    # ------------------ State and Controls ------------------
    
    targets = ["Final Capital", "Starting Capital", "Interest Rate", "Duration", "Monthly Contribution"]

    combo = ft.Dropdown(
        options=[ft.dropdown.Option(target) for target in targets],
        label="Was soll berechnet werden?",
        value="Final Capital",
        width=250
    )

    fields = {
        "Starting Capital": ft.TextField(label="Starting Capital", value="1000", suffix_text="€", keyboard_type=ft.KeyboardType.NUMBER),
        "Interest Rate": ft.TextField(label="Interest Rate", value="5", suffix_text="% p.a.", keyboard_type=ft.KeyboardType.NUMBER),
        "Duration": ft.TextField(label="Duration", value="10", suffix_text="Jahre", keyboard_type=ft.KeyboardType.NUMBER),
        "Final Capital": ft.TextField(label="Final Capital", suffix_text="€", keyboard_type=ft.KeyboardType.NUMBER),
        "Monthly Contribution": ft.TextField(label="Monthly Contribution", value="50", suffix_text="€", keyboard_type=ft.KeyboardType.NUMBER),
    }

    label_result = ft.Text("", size=18, weight=ft.FontWeight.BOLD, color=Colors.BLUE_700)

    # ------------------ Helper Functions ------------------

    def get_input_value(label: str):
        """Helper to safely get float value from input fields."""
        entry = fields[label]
        
        try:
            if entry.disabled:
                return 0.0 if label in ["Starting Capital", "Monthly Contribution"] else None
            
            # Verwende replace, um Kommas für deutsche Eingaben zu verarbeiten
            return float(entry.value.replace(',', '.'))
        except ValueError:
            raise ValueError(f"Ungültige Eingabe in '{entry.label}'")
        except KeyError:
            return 0.0


    def update_input_fields(e: ControlEvent = None):
        """Enable all input fields except the one being calculated."""
        target = combo.value
        
        for label, entry in fields.items():
            is_target = label == target
            entry.disabled = is_target
            entry.opacity = 0.5 if is_target else 1.0
            
            # Standardwerte setzen/löschen
            if is_target:
                entry.value = ""
            elif not entry.value:
                if label == "Starting Capital": entry.value = "0"
                elif label == "Duration": entry.value = "1"
                elif label == "Interest Rate": entry.value = "0"

        page.update()

    # Weisen Sie die Update-Funktion dem Dropdown zu
    combo.on_change = update_input_fields
    update_input_fields() # Initial call

    # ------------------ Main Calculation Logic ------------------

    def perform_calculation(e: ControlEvent):
        target = combo.value
        result = None
        
        try:
            starting_capital = get_input_value("Starting Capital")
            interest = get_input_value("Interest Rate")
            years = get_input_value("Duration")
            final_capital = get_input_value("Final Capital")
            contribution = get_input_value("Monthly Contribution")
            
            # --- Calculation Dispatch ---

            if target == "Final Capital":
                result = calculate_final_capital(starting_capital, interest, years, contribution)
                label_result.value = f"Endkapital: €{result:.2f}"
            
            elif target == "Starting Capital":
                if final_capital is None: raise ValueError("Final Capital fehlt.")
                result = calculate_starting_capital(final_capital, interest, years, contribution)
                label_result.value = f"Startkapital: €{result:.2f}"
            
            elif target == "Interest Rate":
                if final_capital is None: raise ValueError("Final Capital fehlt.")
                result = calculate_interest_rate(starting_capital, years, final_capital, contribution)
                if result is not None:
                    label_result.value = f"Zinssatz: {result:.4f}% p.a."
                else:
                    label_result.value = "Zinssatz konnte nicht ermittelt werden."
            
            elif target == "Duration":
                if final_capital is None: raise ValueError("Final Capital fehlt.")
                result = calculate_years(starting_capital, interest, final_capital, contribution)
                if result is not None:
                    label_result.value = f"Dauer: {result:.1f} Jahre"
                else:
                    label_result.value = "Dauer konnte nicht ermittelt werden."
            
            elif target == "Monthly Contribution":
                if final_capital is None: raise ValueError("Final Capital fehlt.")
                result = calculate_monthly_contribution(starting_capital, interest, years, final_capital)
                label_result.value = f"Monatsbeitrag: €{result:.2f}"

        except ValueError as ex:
            label_result.value = f"Fehler: {ex}"
        except Exception as ex:
            label_result.value = f"Ein unerwarteter Fehler ist aufgetreten."
            
        page.update()

    # ------------------ Layout Assembly ------------------

    # Der Berechnen-Button
    calculate_button = ft.ElevatedButton(
        text="Berechnen",
        on_click=perform_calculation,
        bgcolor=Colors.GREEN_700,
        color=Colors.WHITE,
        width=250
    )

    # Fügt alle Elemente zur Seite hinzu
    page.add(
        ft.Text("Zinsrechner", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Container(combo, padding=ft.padding.only(bottom=15)),
        
        # Input fields in einer vertikalen Spalte
        ft.Column([fields[label] for label in targets], spacing=10),
        
        ft.Container(calculate_button, padding=ft.padding.only(top=15, bottom=15)),
        label_result
    )


if __name__ == "__main__":
    ft.app(target=main)