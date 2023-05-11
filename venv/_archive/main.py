import os
import time
import requests
import zipfile
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import imageio
import schedule

def download_zip_file(url, output_path):
    response = requests.get(url)
    with open(output_path, 'wb') as f:
        f.write(response.content)

def extract_csv_from_zip(zip_path, csv_filename, output_dir):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith(csv_filename):
                zip_ref.extract(file, output_dir)
                return os.path.join(output_dir, file)

def load_csv_to_dataframe(csv_path):
    return pd.read_csv(csv_path)

def create_visualization(df, output_image_path):
    # Replace the following line with your specific seaborn visualization code
    sns.barplot(x='categorical_variable', y='numerical_variable', data=df)

    plt.savefig(output_image_path)
    plt.close()

def create_animation(image_paths, output_gif_path, fps=1):
    images = [imageio.imread(img_path) for img_path in image_paths]
    imageio.mimsave(output_gif_path, images, fps=fps)

output_images = []

def job():
    # Set the URL of the zip file and the path where you want to save it
    url = "https://example.com/data.zip"
    zip_path = "data.zip"

    # Download the zip file
    download_zip_file(url, zip_path)

    # Set the CSV filename and the directory where you want to save it
    csv_filename = "data.csv"
    output_dir = "output"

    # Extract the CSV file
    csv_path = extract_csv_from_zip(zip_path, csv_filename, output_dir)

    # Load the CSV data into a pandas DataFrame
    df = load_csv_to_dataframe(csv_path)

    # Create a visualization and save it as an image
    output_image_path = os.path.join(output_dir, f"{time.strftime('%Y%m%d_%H%M%S')}.png")
    create_visualization(df, output_image_path)
    output_images.append(output_image_path)

# Schedule the job to run twice a day
schedule.every().day.at("09:00").do(job)
schedule.every().day.at("21:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(60)

# After enough images have been generated, create an animated GIF
output_gif_path = "output/visualization_animation.gif"
create_animation(output_images, output_gif_path, fps=1)
