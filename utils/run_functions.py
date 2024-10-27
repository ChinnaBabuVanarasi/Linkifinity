from utils.links_csv import csv_links_function
from utils.manga_chapters import manga_chapters_function
from utils.manga_details import manga_details_function
from utils.manga_links import manga_links_function

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