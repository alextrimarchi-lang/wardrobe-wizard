import json
import os
import random
from PIL import Image
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk

CLOSET_FILENAME = "test-closet.json"
IMAGES_PATH = "images"

# telling my code what my outfit needs to contain - all outfits need a top, bottom and shoe
class Outfit:
    def __init__(self, policy, closet):
        self.policy = policy
        self.order = ["top", "bottom", "shoe"]
        self.piece_type_to_list = {
            "top": closet["tops"],
            "bottom": closet["bottoms"],
            "shoe": closet["shoes"]
        }

    def generate(self):
        self.__randomize_piece_lists()
        outfit = self.__get_valid_outfit()


        # Display images
        self.__display_outfit([outfit[piece]["filename"] for piece in self.order])
        return outfit



    def __randomize_piece_lists(self):
        for piece_type, lst in self.piece_type_to_list.items():
            self.piece_type_to_list[piece_type] = random.sample(lst, len(lst))

    def __get_valid_outfit(self):
        first_piece_type = self.order[0]
        to_explore = [(first_piece_type, p) for p in self.piece_type_to_list[first_piece_type]]
        outfit = {}

        while to_explore:
            piece_type, piece = to_explore.pop()
            outfit[piece_type] = piece

            if self.policy.is_valid(**outfit):
                if len(outfit) == len(self.order):
                    return outfit
                next_piece_type = self.__get_next_piece_type(piece_type)
                to_explore.extend(
                    [(next_piece_type, p) for p in self.piece_type_to_list[next_piece_type]]
                )
            else:
                del outfit[piece_type]

        raise Exception("Cannot generate outfit with current closet and constraints.")

    def __display_outfit(self, filenames):
        # Resize images to same size to avoid errors
        images = [Image.open(os.path.join(IMAGES_PATH, f)).resize((200, 200)) for f in filenames]
        image_stack = np.hstack(images)


    def __get_next_piece_type(self, curr_piece_type):
        return self.order[self.order.index(curr_piece_type) + 1]

# what criteria each piece of clothing needs to meet to qualify for my outfit genarated
class OutfitPolicy:
    def __init__(self, Casual=False, Going_Out=False, Hot=False, Cold=False, closet=None):
        self.Casual_required = Casual
        self.Going_Out_required = Going_Out
        self.Hot_required = Hot
        self.Cold_required = Cold
        self.piece_type_to_list = {
            "top": closet["tops"],
            "bottom": closet["bottoms"],
            "shoe": closet["shoes"]
        }


    def is_valid(self, top=None, bottom=None, shoe=None):
        pieces = {"top": top, "bottom": bottom, "shoe": shoe}

        for piece_type, piece in pieces.items():
            if piece is None:
                continue
            attr = piece["attributes"]
            if self.Casual_required and not attr.get("Casual", False):
                return False
            if self.Going_Out_required and not attr.get("Going Out", False):
                return False
            if self.Hot_required and not attr.get("Hot", False):
                return False
            if self.Cold_required and not attr.get("Cold", False):
                return False

        return True




def main():
    with open(CLOSET_FILENAME, "r") as f:
        closet = json.load(f)

    root = tk.Tk()
    root.title("Wardrobe Wizard - Outfit Generator")
    root.geometry("1000x1000")
    root.configure(bg="#D8B4E2")  # light purple colour

    tk.Label(root, text="Select Your Outfit Style:", font=("Comic Sans MS", 20)).pack(pady=20)
    style_var = tk.StringVar(value="Click Here")
    style_menu = ttk.Combobox(root, textvariable=style_var, values=["Casual", "Going Out"], state="readonly")
    style_menu.pack()

    tk.Label(root, text="Select Weather:", font=("Comic Sans MS", 20)).pack(pady=25)
    weather_var = tk.StringVar(value="Click Here")
    weather_menu = ttk.Combobox(root, textvariable=weather_var, values=["Hot", "Cold"], state="readonly")
    weather_menu.pack()

    result_label = tk.Label(root, text="", font=("Arial", 25))
    result_label.pack(pady=15)

    image_frame = tk.Frame(root)
    image_frame.pack()

    def display_outfit_images(filenames):
        # Clear previous images
        for widget in image_frame.winfo_children():
            widget.destroy()

        for filename in filenames:
            img_path = os.path.join(IMAGES_PATH, filename)
            img = Image.open(img_path).resize((150, 150))
            img_tk = ImageTk.PhotoImage(img)
            lbl = tk.Label(image_frame, image=img_tk)
            lbl.image = img_tk
            lbl.pack(side="left", padx=5)

    def generate_outfit():
        try:
            policy = OutfitPolicy(
                Casual=(style_var.get() == "Casual"),
                Going_Out=(style_var.get() == "Going Out"),
                Hot=(weather_var.get() == "Hot"),
                Cold=(weather_var.get() == "Cold"),
                closet=closet
            )
            outfit = Outfit(policy, closet).generate()
            names = ", ".join([outfit[p]["name"] for p in ["top", "bottom", "shoe"]])
            result_label.config(text=f"Your Outfit: {names}")
            display_outfit_images([outfit[p]["filename"] for p in ["top", "bottom", "shoe"]])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(root, text="Generate Outfit", command=generate_outfit, font=("Comic Sans MS", 25), bg="#05000a", fg="black").pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()
