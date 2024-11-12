from utils.links_csv import csv_links_function
from utils.manga_chapters import manga_chapters_function
from utils.manga_details import manga_details_function
from utils.manga_links import manga_links_function


def run_manga_funcs(choice=0):
    if choice == 0:
        # running csvlinks function
        print('---------------------------Started CSV Data-------------------------------------')
        csv_links_function(0)
        print('---------------------------Started LINKS Data-----------------------------------')
        # running manga links function
        manga_links_function()
        print('---------------------------Started DETAILS Data---------------------------------')
        # running manga details function
        manga_details_function()
        print('---------------------------Started CHAPTERS Data--------------------------------')
        # running manga chapters function
        manga_chapters_function()
    else:
        print('---------------------------Started CHAPTERS Data--------------------------------')
        # running manga chapters function
        manga_chapters_function()


choice_to_run = 1
run_manga_funcs(choice_to_run)