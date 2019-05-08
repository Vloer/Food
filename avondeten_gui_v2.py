#! python3
'''
TODO complete dish removes all other options from the grid and >>vice versa<<<
TODO friet multiplier knop
'''
import os
import pandas as pd
import numpy as np
from tkinter import *
from tkinter import messagebox
import time
from math import ceil
import sys
from PIL import ImageTk, Image

######################## TKinter stuff  #########################################
# Initialize
app = Tk()
app.geometry('700x166')
app.title('Avondeten GUI')
all_entries = {'carbs': [],
               'protein': [],
               'vegetables': [],
               'complete_dish': [],
               'mltp': []}
all_entries_to_save = {'carbs': [],
                       'protein': [],
                       'vegetables': [],
                       'complete_dish': [],
                       'mltp': []}
food_categories = {'carbs': ['Aardappels', 'Pasta', 'Rijst', 'Misc'],
                   'protein': ['Vlees', 'Vis', 'Vlees_los'],
                   'vegetables': ['Groenten_los', 'Salade'],
                   'complete_dish': ['Aardappels_c', 'Pasta_c', 'Rijst_c', 'Misc_c']}

# Default save file path
save_path = os.path.abspath('')
food_data_filename = 'avondeten_data'
h5_file = os.path.join(save_path, food_data_filename + '.h5')

input_save_path = StringVar()
input_food_data_filename = StringVar()


########################################################
#################### Base functions ####################
########################################################
def client_exit():
    if messagebox.askyesno('Exit', 'Are you sure you want to exit?', icon='warning'):
        exit()


def clear_all():
    for widget in mainframe.winfo_children():
        widget.pack_forget()
        widget.grid_forget()
        widget.place_forget()


def print_nothing():
    print('Nothing happens')


def set_text(entry, text):
    entry.delete(0, END)
    entry.insert(0, text)
    return


def get_row_sizes(data_table):
    size = data_table.shape

    # Find longest row (least empty cells)
    count_array = np.zeros(size[0])
    row_sizes = np.zeros(size[0])
    for row in range(size[0]):
        for col in range(size[1]):
            if not data_table[col][row]:  # convert NoneType to empty string. Leave this in else it doesnt work
                if type(data_table[col][row]) == np.float64:
                    data_table[col][row] = 0
                else:
                    data_table[col][row] = ''
            if not data_table[col][row] == '':
                count_array[row] += 1
        row_sizes[row] = ceil(count_array[row] / 5)  # Number of rows is a multiple of 5
        if row_sizes[row] == 0:  # create 1 empty row if there are no values (shouldnt happen)
            row_sizes[row] = 1
    row_sizes = row_sizes.astype(int)
    return row_sizes


def create_grid(name, data_table, check, extra_row):
    # print('@@@@@@@@@@@@@@@@@@@@@@@@@@CREATE GRID@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    # Before executing check if changes have been made and were saved
    if check:
        if check_changes():
            save_changes()
            # pass
    clear_all()

    # Read table and determine size
    size = data_table.shape
    row_sizes = get_row_sizes(data_table)
    row_sizes[extra_row] += 1

    # Convert None's and Nan's to '' and 0
    for row in range(size[0]):
        for col in range(size[1]):
            try:
                if not data_table[col][row]:
                    data_table[col][row] = ''
            except:
                pass

    # Create index
    for i in range(10):
        Label(mainframe, text='').grid(row=i, column=0)  # empty left top corner
    for row in range(size[0]):
        Label(mainframe, text=data_table.index[row]).grid(row=sum(row_sizes[:row]) + 1, column=0,
                                                          sticky=W)
    for col in range(np.clip(size[1], 0, 5)):
        Label(mainframe, text=col).grid(row=0, column=col + 1, padx=5)

    # Create empty cells
    all_entries[name] = []
    count = 0
    for idx in range(size[0]):
        rows_to_make = row_sizes[idx]
        all_entries[name].append([])
        colcount = 0
        for row in range(rows_to_make):
            count += 1
            if name == 'mltp':
                tbl_length = 4
            else:
                tbl_length = 5
            for col in range(tbl_length):
                all_entries[name][idx].append(Entry(mainframe))
                all_entries[name][idx][colcount].grid(row=count, column=col + 1)
                colcount += 1

    # Convert data to dict and fill with empty values where necessary
    text = data_table.to_dict('split')['data']
    row_sizes_5 = np.asarray(row_sizes) * np.clip(size[1], 0, 5)
    for row in range(size[0]):
        if len(text[row]) > row_sizes_5[row]:
            text[row] = text[row][:row_sizes_5[row]]
        else:  # add empty values
            [text[row].append('') for _ in range(row_sizes_5[row] - len(text[row]))]
    # print(text)

    # Insert saved text
    for row in range(size[0]):
        for col in range(row_sizes_5[row]):
            try:
                set_text(all_entries[name][row][col], text[row][col])
            except IndexError:  # text doesnt exist in DF
                set_text(all_entries[name][row][col], '')


def check_changes():
    # print('@@@@@@@@@@@@@@@@@@@@@@@@@@CHECK CHANGES@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    # Check current input fields versus saved values in h5_file for all tables
    # If changes have been made ANYWHERE, save_file is true and all grids will be saved
    save_file = False
    for name in all_entries.keys():
        data_table = pd.read_hdf(h5_file, key=name)
        size = data_table.shape
        row_sizes = get_row_sizes(data_table)
        row_sizes_5 = np.asarray(row_sizes) * np.clip(size[1], 0, 5)
        try:
            for row in range(size[0]):
                for col in range(row_sizes_5[row]):
                    try:
                        if str(data_table[col][row]) == 'nan':
                            data_table[col][row] = 0
                        saved_text = str(data_table[col][row])
                    except KeyError as e:  # data table is missing empty columns, so change and save that
                        print('KeyError passed at {} row{} : {}'.format(name, row, e))
                        data_table[col] = ''
                        save_file = True
                        pass
                    input_text = all_entries[name][row][col].get()

                    # Compare values
                    if input_text == '':
                        continue
                    elif saved_text != input_text:
                        try:
                            data_table[col][row] = input_text
                        except ValueError:
                            # messagebox.showerror('Incorrect input',
                            #                      'Please insert a number in input field [{}][{}] before continuing'.format(
                            #                          row,col), icon='warning')
                            pass
                        save_file = True
                        print('Changes have been made in table \'{}\': {} at col/row [{}][{}]'.format(name,
                                                                                                      str(input_text),
                                                                                                      str(col),
                                                                                                      str(row)))
        except IndexError as e:
            print('IndexError passed at {}: {}'.format(name, e))
            pass
    return save_file


def save_changes():
    # print('@@@@@@@@@@@@@@@@@@@@@@@@@@SAVE CHANGES@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    # Convert cell values back to dataframe WITH correct index names
    for name in all_entries.keys():
        all_entries_to_save[name] = []  # reset array
        data_table = pd.read_hdf(h5_file, key=name)

        # Create new list to save to dataframe
        try:
            for row in range(len(all_entries[name])):
                all_entries_to_save[name].append([])
                for col in range(np.size(all_entries[name][row])):
                    try:
                        all_entries_to_save[name][row].append(all_entries[name][row][col].get())
                    except IndexError:
                        print('Not enough columns({}) at row {}, moving on'.format(col, row))
                        pass
        except IndexError as e:
            print('IndexError at {}, create new list in all entries to save: {}'.format(name, e))
            pass

        if not check_mltp_input(name):  # if function is NOT valid (there is text, so returns false) don't save
            return
        # if not check_mltp_total(name):
        #     return

        try:
            # Create dataframe to save
            df = pd.DataFrame.from_records(all_entries_to_save[name])  # make frame
            df = df.set_index([data_table.index])  # set index names
        except ValueError as e:
            print('ValueError create dataframe {}: {}'.format(name, e))
            pass

        # print(all_entries_to_save)
        if not df.empty:  # dont overwrite dataframe with an empty one
            print(df)
            with pd.HDFStore(h5_file) as file:
                df.to_hdf(file, key=name, mode='a')
            print('Saved changes in {}'.format(name))


def save_changes_confirmation():
    if messagebox.askyesno('Save', 'Are you sure you want to save?', icon='warning'):
        save_changes()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS,
        # and places our data files in a folder relative to that temp
        # folder named as specified in the datas tuple in the spec file
        base_path = os.path.join(sys._MEIPASS, 'img')
        print('sys meipass')
    except Exception:
        # sys._MEIPASS is not defined, so use the original path
        base_path = os.path.join(save_path, 'images')
        print('niet sys meipass')

    return os.path.join(base_path, relative_path)


#############################################################
#################### Randomize functions ####################
#############################################################
def roll_random_type(name):
    df = pd.read_hdf(h5_file, key=name)  # Food table
    mltp = pd.read_hdf(h5_file, key='mltp')  # Multiplier table
    multiplier = list(mltp.loc[name + '_m'])  # List of multiplier values
    multiplier = [x for x in multiplier if str(x) != 'nan']  # remove nan where possible
    total = sum(multiplier)
    multiplier = np.array(multiplier) / total
    food_type = np.random.choice(df.index, p=multiplier)  # get random food type
    return food_type


def roll_random_food(name, type):
    df = pd.read_hdf(h5_file, key=name)  # Food table
    while True:
        result = np.random.choice(df.loc[type])
        if result:
            return result


############################################################
#################### Buttons, menus etc ####################
############################################################
def file_path():
    clear_all()
    Label(mainframe, text='Data file path: ', font=('Helvetica', 15)).place(anchor=NW, relx=0, rely=0)
    Label(mainframe, text='Data file name: ', font=('Helvetica', 15)).place(anchor=NW, relx=0, rely=0.25)
    Label(mainframe, text='Complete file path: ', font=('Helvetica', 12)).place(anchor=NW, relx=0, rely=0.75)

    global path_entry
    global filename_entry
    path_entry = Entry(mainframe, width=50, textvariable=input_save_path)
    path_entry.place(anchor=NW, relx=0.25, rely=0.025)
    input_save_path.set(save_path)
    filename_entry = Entry(mainframe, width=50, textvariable=input_food_data_filename)
    filename_entry.place(anchor=NW, relx=0.25, rely=0.275)
    input_food_data_filename.set(food_data_filename)

    global complete_file
    global complete_txt
    try:
        complete_file = os.path.join(path_entry.get(), filename_entry.get() + '.h5')
        complete_txt = Label(mainframe, text=complete_file, font=('Helvetica', 12))
        complete_txt.place(anchor=NW, relx=0.25, rely=0.75)
    except AttributeError:
        pass
    try:
        update_button.place(anchor=NE, relx=0.9, rely=0.25)
    except NameError:
        pass


def update_savepath():
    global save_path
    global food_data_filename
    global h5_file
    global complete_txt

    save_path = input_save_path.get()
    food_data_filename = input_food_data_filename.get()
    h5_file = os.path.join(save_path, food_data_filename + '.h5')
    complete_txt.place_forget()
    complete_txt = Label(mainframe, text=h5_file, font=('Helvetica', 12))
    complete_txt.place(anchor=NW, relx=0.25, rely=0.75)

    if create_base_file():
        messagebox.showinfo('', 'New file created', icon='warning')


def show_carbs():
    data_table = pd.read_hdf(h5_file, key='carbs')
    create_grid('carbs', data_table, True, False)


def show_protein():
    data_table = pd.read_hdf(h5_file, key='protein')
    create_grid('protein', data_table, True, False)


def show_vegetables():
    data_table = pd.read_hdf(h5_file, key='vegetables')
    create_grid('vegetables', data_table, True, False)


def show_complete_dishes():
    data_table = pd.read_hdf(h5_file, key='complete_dish')
    create_grid('complete_dish', data_table, True, False)


def show_mltp():
    data_table = pd.read_hdf(h5_file, key='mltp')
    # data_table = np.round(data_table[:] * 100, 2)
    create_grid('mltp', data_table, True, False)


def check_mltp_input(name):
    if name == 'mltp':
        data = all_entries_to_save[name]
        for row in range(len(data)):
            for col in range(len(data[row])):
                try:
                    data[row][col] = float(data[row][col])
                except ValueError:
                    messagebox.showerror('Incorrect input',
                                         'Please insert a number in input field [{}][{}] before continuing'.format(
                                             row, col), icon='warning')
                    return False
        return True
    return True


def check_mltp_total(name):
    if name == 'mltp':
        # Convert numbers to float if possible, then check sum per row seperately. Exit if sum != ~1
        data = all_entries_to_save[name]
        for row in range(len(data)):
            for col in range(len(data[row])):
                data[row][col] = float(data[row][col])
            total = round(np.nansum(data[row]), 1)
            if total != 1:
                messagebox.showerror('Incorrect input',
                                     'Sum of all column values should equal 1. Row {} has a total value of {}'
                                     .format(row, total), icon='warning')
                return False
        return True
    return True


def randomize():
    clear_all()
    [print_text('a', '', i) for i in [0, 0.25, 0.5, 0.75]]  # create empty text box
    rand_button_all.place(anchor=E, relx=1, rely=0.5, relwidth=0.25, relheight=1)
    rand_button_carbs.place(anchor=NW, relx=0, rely=0, relwidth=0.25, relheight=0.25)
    rand_button_protein.place(anchor=NW, relx=0, rely=0.25, relwidth=0.25, relheight=0.25)
    rand_button_vegetables.place(anchor=NW, relx=0, rely=0.5, relwidth=0.25, relheight=0.25)
    rand_button_complete.place(anchor=NW, relx=0, rely=0.75, relwidth=0.25, relheight=0.25)


def print_text(name, text, rely):
    name = Label(mainframe, text=text, font=('Helvetica', 20))
    name.place(anchor=N, relx=0.5, rely=rely, relwidth=0.5, relheight=0.25)


def rand_all():
    # Clear all fields
    for widget in mainframe.winfo_children():
        if 'text' in str(widget):
            widget.place_forget()
        elif 'label' in str(widget):
            widget.place_forget()

    num = np.random.random()
    if num < 0.05:
        rand_friet()
    elif num < 0.30:
        rand_complete()
    else:
        rand_carbs()
        rand_protein()
        rand_vegetables()


def rand_carbs():
    text = roll_random_food('carbs', roll_random_type('carbs'))
    print_text('carbs_text', text, 0)


def rand_protein():
    text = roll_random_food('protein', roll_random_type('protein'))
    print_text('protein_text', text, 0.25)


def rand_vegetables():
    text = roll_random_food('vegetables', roll_random_type('vegetables'))
    print_text('vegetables_text', text, 0.5)


def rand_complete():
    for widget in mainframe.winfo_children():
        if 'text' in str(widget):
            widget.place_forget()
        elif 'label' in str(widget):
            widget.place_forget()
    text = roll_random_food('complete_dish', roll_random_type('carbs'))
    print_text('complete_text', text, 0.75)


def rand_friet():
    global img
    food = np.random.choice(['friet', 'kebab', 'pannekoeken', 'pizza'])
    img = ImageTk.PhotoImage(Image.open(resource_path(food + '.jpg')))
    img_label = Label(mainframe, image=img)
    img_label.place(anchor=N, relx=0.5, rely=0, relwidth=0.5, relheight=1)


def conditionals():
    print_nothing()


def add_column(name):
    for key in food_categories.keys():
        if name in food_categories[key]:
            food_cat = key
            break
    idx = food_categories[key].index(name)  # find row number to add extra values to
    df = pd.read_hdf(h5_file, key=food_cat)
    print('Creating grid with extra column for {}'.format(name))
    create_grid(food_cat, df, True, idx)


#####################################################################################
#################### Check if save file exists, else create base ####################
#####################################################################################
def create_base_file():
    if not os.path.isfile(h5_file):
        food_list = {
            'carbs': {
                'Aardappels': ['Gekookte aardappels', 'Gebakken aardappels', 'Aardappelpuree', '', '', '', '', '', '',
                               ''],
                'Pasta': ['Spaghetti', 'Tagliatelle', 'Schroeven', 'Farfalle', 'Schelpen (pasta)', 'Penne', 'Mie', '',
                          '', ''],
                'Rijst': ['Risotto', 'Witte rijst', '', '', '', '', '', '', '', ''],
                'Misc': ['Burrito', 'Wraps', 'Taco', '', '', '', '', '', '', '']
            },
            'protein': {
                'Vlees': ['Varkensvlees', 'Kip', 'Spek', 'Gehakt', '', '', '', '', '', ''],
                'Vis': ['Pangasius filet', 'Garnalen', 'Zalm', 'Kabeljauw', '', '', '', '', '', ''],
                'Vlees_los': ['Biefstuk', 'Schnitzel', 'Cordon Bleu', 'Varkenslapjes', 'Spareribs', 'Worst',
                              'Gehaktbal', '', '', '']
            },
            'vegetables': {
                'Groenten_los': ['Broccoli', 'Witlof', 'Rode kool', 'Erwtjes en wortels', 'Zuurkool', 'Sperziebonen',
                                 'Capucijners', '', '', ''],
                'Salade': ['Salade', '', '', '', '', '', '', '', '', '']
            },
            'complete_dish': {
                'Aardappels': ['Boerenkoolstamp', 'Wortelstamp', 'Zuurkoolstamp', '', '', '', '', '', '', ''],
                'Pasta': ['Pasta Carbonara', 'Pasta Bolognese', '', '', '', '', '', '', '', ''],
                'Rijst': ['Bobotie', 'Curry', 'Nasi', 'Paella', 'Sushi', '', '', '', '', ''],
                'Misc': ['Ovenschotel', 'Rode kool schotel', 'Bloemkoolpizza', '', '', '', '', '', '', '']
            }
        }
        multi_dict = {
            'carbs_m': np.array([1 / 4, 1 / 4, 1 / 4, 1 / 4]),  # aardappels pasta rijst wraps
            'protein_m': np.array([1 / 3, 1 / 3, 1 / 3]),  # vlees vis vlees_los
            'vegetables_m': np.array([9 / 10, 1 / 10]),  # groenten_los salade
            'complete_dish_m': np.array([1 / 3, 1 / 3, 1 / 3])}  # stamp compleet ovenschotel

        # Save all categories in a datafile specified by food_data_filename
        def save_to_file():
            for name in food_list.keys():
                df = pd.DataFrame.from_dict(food_list[name], orient='index')
                with pd.HDFStore(h5_file) as file:
                    df.to_hdf(file, key=name, mode='a')

            df = pd.DataFrame.from_dict(multi_dict, orient='index')
            with pd.HDFStore(h5_file) as file:
                df.to_hdf(file, key='mltp', mode='a')
            # To read: pd.read_hdf(h5_file, key='mltp')

        save_to_file()
        return True
    else:
        return False


create_base_file()

#######################################################
#################### Create layout ####################
#######################################################
# Create master frame
mainframe = Frame(app)
mainframe.pack(fill=BOTH, expand=1)

# Create menu
mainmenu = Menu(app)
app.config(menu=mainmenu)

# Add file option
file = Menu(mainmenu, tearoff=False)
file.add_command(label='File path', command=file_path)
file.add_command(label='Clear all', command=clear_all)
file.add_command(label='Exit app', command=client_exit)
mainmenu.add_cascade(label='File', menu=file)

# Add save button
mainmenu.add_command(label='Save changes', command=save_changes_confirmation)

# Add food lists
food = Menu(mainmenu, tearoff=False)
food.add_command(label='Carbs', command=show_carbs)
food.add_command(label='Protein', command=show_protein)
food.add_command(label='Vegetables', command=show_vegetables)
food.add_command(label='Complete dishes', command=show_complete_dishes)
mainmenu.add_cascade(label='Food list', menu=food)

# Add column button
column_menu = Menu(mainmenu, tearoff=False)

column_carbs = Menu(column_menu, tearoff=False)
column_carbs.add_command(label='Aardappels', command=lambda: add_column('Aardappels'))
column_carbs.add_command(label='Pasta', command=lambda: add_column('Pasta'))
column_carbs.add_command(label='Rijst', command=lambda: add_column('Rijst'))
column_carbs.add_command(label='Misc', command=lambda: add_column('Misc'))

column_protein = Menu(column_menu, tearoff=False)
column_protein.add_command(label='Vlees', command=lambda: add_column('Vlees'))
column_protein.add_command(label='Vis', command=lambda: add_column('Vis'))
column_protein.add_command(label='Vlees_los', command=lambda: add_column('Vlees_los'))

column_vegetables = Menu(column_menu, tearoff=False)
column_vegetables.add_command(label='Groenten_los', command=lambda: add_column('Groenten_los'))
column_vegetables.add_command(label='Salade', command=lambda: add_column('Salade'))

column_complete = Menu(column_menu, tearoff=False)
column_complete.add_command(label='Aardappels', command=lambda: add_column('Aardappels_c'))
column_complete.add_command(label='Pasta', command=lambda: add_column('Pasta_c'))
column_complete.add_command(label='Rijst', command=lambda: add_column('Rijst_c'))
column_complete.add_command(label='Misc', command=lambda: add_column('Misc_c'))

mainmenu.add_cascade(label='Add column', menu=column_menu)
column_menu.add_cascade(label='Carbs', menu=column_carbs)
column_menu.add_cascade(label='Protein', menu=column_protein)
column_menu.add_cascade(label='Vegetables', menu=column_vegetables)
column_menu.add_cascade(label='Complete dish', menu=column_complete)

# Add multipliers
mainmenu.add_command(label='Multipliers', command=show_mltp)

# Add conditionals
# mainmenu.add_command(label='Conditionals', command=conditionals)

# Add randomizer
mainmenu.add_command(label='Randomize!', command=randomize)

# Randomize buttons
rand_button_all = Button(mainframe, text='RANDOMIZE', font=('Helvetica', 18, 'bold'), command=rand_all,
                         overrelief=RIDGE)
rand_button_carbs = Button(mainframe, text='Carbs', command=rand_carbs, overrelief=RIDGE,
                           fg='DarkGoldenRod2')
rand_button_protein = Button(mainframe, text='Protein', command=rand_protein, overrelief=RIDGE,
                             fg='red')
rand_button_vegetables = Button(mainframe, text='Vegetables', command=rand_vegetables,
                                overrelief=RIDGE, fg='green')
rand_button_complete = Button(mainframe, text='Complete dish', command=rand_complete,
                              overrelief=RIDGE)

# Add file path screen
file_path()
update_button = Button(mainframe, text='Update', fg='red', font=('Helvetica', 20), command=update_savepath)
update_button.place(anchor=NE, relx=0.9, rely=0.25)

# Run program
app.mainloop()
