import os

archivo = r"C:\Users\Tenshi\Desktop\Repocision_Proyecto\Inversion.xlsx"
if os.path.exists(archivo):
    print("El archivo existe.")
else:
    print("El archivo no existe.")