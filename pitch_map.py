import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd
import zipfile
import os
from io import BytesIO

match_type_mapping = {
         1: "Test Match",
        2: "One-Day International",
        3: "Twenty20 International",
        4: "First Class Match",
        5: "List A Match",
        6: "Twenty20 Match",
        7: "Others",
        8: "Women's Tests",
        9: "Women's One-Day Internationals",
        10: "Women's Twenty20 Internationals",
        11: "Other First Class",
        12: "Other List A",
        13: "Other Twenty20",
        14: "Women's First Class Matches",
        15: "Women's List A Matches",
        16: "Women's Twenty20",
        17: "Others Women's First Class",
        18: "Others Women's List A",
        19: "Others Women's Twenty20",
        20: "Youth Tests",
        21: "Youth One-Day Internationals",
        22: "Youth Twenty20 Internationals",
        26: "Youth First Class",
        27: "Youth List A",
        28: "Youth Twenty20",
        29: "Women's Youth Tests",
        30: "Women's Youth One-Day Internationals",
        31: "Women's Youth Twenty20 Internationals",
        32: "Women's Youth First Class",
        33: "Women's Youth List A",
        34: "Women's Youth Twenty20",
        35: "Other Youth First Class Matches",
        36: "Other Youth List A Matches",
        37: "Dual Collection Fast Test Format",
        38: "Dual Collection Fast ODI Format",
        39: "Dual Collection Fast T20 Format",
        40: "Other Youth Twenty20 Matches",
        41: "International The Hundred",
        42: "Domestic The Hundred",
        43: "Women's International The Hundred",
        44: "Women's Domestic The Hundred",
        45: "Youth Women's T20",
        50: "T10",
        51: "W T10",
        53: "Others U19 Women T20",
        54: "Other Women's Youth Twenty20",
        91: "The 6ixty"
    }
def calculate_pitch_map_coordinates(length_x, length_y, origin_x, origin_y, is_1s, is_2s, is_4s, is_6s, is_0s, is_batwkts):
    x_axis = calculate_pitch_map_xaxis(length_x, length_y, origin_x)
    y_axis = calculate_pitch_map_yaxis(length_y, origin_y)

    if is_batwkts == 1:
             color = 'azure'
    elif is_4s == 1:
             color = 'darkblue'
    elif is_6s == 1:
             color = 'red'
    elif is_0s == 1:
             color = 'black'
    elif is_1s == 1:
             color = 'goldenrod'
    elif is_2s == 1:
             color = 'purple'
    elif is_3s == 1:
             color = 'green'
    else:
             color = 'brown'

    
    return x_axis, y_axis, color

def calculate_pitch_map_xaxis(length_x, length_y, origin_x):
    return ((pitch_map_start_x2p - pitch_map_start_x1p) / old_reg_xlen) * length_x + pitch_map_start_x1p

def calculate_pitch_map_yaxis(length_y, origin_y):
    return pitch_map_height - (((pitch_map_stump_y - pitch_map_start_y) / (old_reg_stump_y - old_reg_start_y)) * (length_y - old_reg_start_y) + pitch_map_start_y)

def filter_data_by_overs(data, overs_phase):
    if overs_phase == 'Power Play (1-6)':
        return data[(data['overs'] >= 0.1) & (data['overs'] <= 5.6)]
    elif overs_phase == 'Middle Overs (7-15)':
        return data[(data['overs'] >= 6.1) & (data['overs'] <= 14.6)]
    elif overs_phase == 'Death Overs (16-20)':
        return data[(data['overs'] >= 15.1) & (data['overs'] <= 19.6)]
    else:  # 'All'
        return data


Copy code
def main():
    st.title("Cricket Pitch Map Visualization")

    csv_path = "NewData.csv"
    data = pd.read_csv(csv_path)
    data = data.dropna(subset=['overs'])
    
    data['Date'] = pd.to_datetime(data['date'])
    
    # Date range filter
    start_date, end_date = st.date_input("Select date range:", [data['Date'].min(), data['Date'].max()])
    filtered_data = data[(data['Date'] >= pd.to_datetime(start_date)) & (data['Date'] <= pd.to_datetime(end_date))]

    # Filter competitions based on date range
    competitions = list(filtered_data['CompName'].unique())
    selected_competition = st.multiselect("Select competition:", competitions)
    
    if selected_competition:
        filtered_data = filtered_data[filtered_data['CompName'].isin(selected_competition)]

    # Filter batsman club names based on competition
    bat_club_names = list(filtered_data['battingclubid'].unique())
    selected_bat_club_name = st.multiselect("Select the batsman's club id:", bat_club_names)
    
    if selected_bat_club_name:
        filtered_data = filtered_data[filtered_data['battingclubid'].isin(selected_bat_club_name)]

    # Filter match ids based on batsman club id
    match_ids = list(filtered_data['matchid'].unique())
    selected_match_id = st.multiselect("Select Match:", match_ids)
    
    if selected_match_id:
        filtered_data = filtered_data[filtered_data['matchid'].isin(selected_match_id)]
    
    # Filter batsman names based on match id
    batsman_names = ['All'] + list(filtered_data['StrikerName'].unique())
    selected_batsman_name = st.multiselect("Select the batsman's name:", batsman_names, default=['All'])
    
    if selected_batsman_name:
        spin_or_pace = st.multiselect("Choose bowler type", ['Pace', 'Spin', 'Both'])
        
        bowler_type = []
        if 'Pace' in spin_or_pace:
            pace_type = st.multiselect("Select Pace Type:", ['RAP', 'LAP', 'Both'])
        if 'Spin' in spin_or_pace:
            spin_type = st.multiselect("Select Spin Type:", ['RAO', 'SLAO', 'RALB', 'LAC', 'Both'])
        
        run_types = st.multiselect("Select run types:", ['0s', '1s', '2s','3s', '4s', '6s', 'wickets', 'All'], default=['All'])
        
        output_dir = 'output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            if 'All' in selected_batsman_name:
                batsmen_to_plot = filtered_data['StrikerName'].unique()
            else:
                batsmen_to_plot = selected_batsman_name
            
            for batsman in batsmen_to_plot:
                filtered_data_batsman = filtered_data[filtered_data['StrikerName'] == batsman]
                
                if 'Pace' in spin_or_pace and 'BowlerType' in filtered_data_batsman.columns:
                    filtered_data_batsman = filtered_data_batsman[filtered_data_batsman['PaceorSpin'] == 1]
                    if 'RAP' in pace_type:
                        filtered_data_batsman = filtered_data_batsman[filtered_data_batsman['BowlerType'] == 'RAP']
                    if 'LAP' in pace_type:
                        filtered_data_batsman = filtered_data_batsman[filtered_data_batsman['BowlerType'] == 'LAP']
                elif 'Spin' in spin_or_pace and 'BowlerType' in filtered_data_batsman.columns:
                    filtered_data_batsman = filtered_data_batsman[filtered_data_batsman['PaceorSpin'] == 2]
                    if 'RAO' in spin_type:
                        filtered_data_batsman = filtered_data_batsman[filtered_data_batsman['BowlerType'] == 'RAO']
                    if 'SLAO' in spin_type:
                        filtered_data_batsman = filtered_data_batsman[filtered_data_batsman['BowlerType'] == 'SLAO']
                    if 'RALB' in spin_type:
                        filtered_data_batsman = filtered_data_batsman[filtered_data_batsman['BowlerType'] == 'RALB']
                    if 'LAC' in spin_type:
                        filtered_data_batsman = filtered_data_batsman[filtered_data_batsman['BowlerType'] == 'LAC']
                
                # Filter run types
                if 'All' not in run_types:
                    conditions = []
                    if '0s' in run_types:
                        conditions.append(filtered_data_batsman['0s'] == 1)
                    if '1s' in run_types:
                        conditions.append(filtered_data_batsman['1s'] == 1)
                    if '2s' in run_types:
                        conditions.append(filtered_data_batsman['2s'] == 1)
                    if '3s' in run_types:
                        conditions.append(filtered_data_batsman['3s'] == 1)
                    if '4s' in run_types:
                        conditions.append(filtered_data_batsman['4s'] == 1)
                    if '6s' in run_types:
                        conditions.append(filtered_data_batsman['6s'] == 1)
                    if 'wickets' in run_types:
                        conditions.append(filtered_data_batsman['Batwkts'] == 1)
                    filtered_data_batsman = filtered_data_batsman[pd.concat(conditions, axis=1).any(axis=1)]
                
                if not filtered_data_batsman.empty:
                    batting_type = filtered_data_batsman['StrikerBattingType'].iloc[0]

                    if batting_type == 1:
                        image_path = 'pitchR.jpg'
                    elif batting_type == 2:
                        image_path = 'pitchL.jpg'
                    
                    img = Image.open(image_path)
                    img_array = plt.imread(image_path)
                    height, width, _ = img_array.shape
                    origin_x, origin_y = 0, 0

                    fig, ax = plt.subplots()
                    ax.imshow(img_array, extent=[0, width, 0, height])

                    for i in range(len(filtered_data_batsman)):
                        pitch_x, pitch_y, point_color = calculate_pitch_map_coordinates(
                            filtered_data_batsman['LengthX'].iloc[i], 
                            filtered_data_batsman['LengthY'].iloc[i], 
                            origin_x, 
                            origin_y, 
                            filtered_data_batsman['1s'].iloc[i], 
                            filtered_data_batsman['2s'].iloc[i], 
                            filtered_data_batsman['4s'].iloc[i], 
                            filtered_data_batsman['6s'].iloc[i],
                            filtered_data_batsman['0s'].iloc[i], 
                            filtered_data_batsman['Batwkts'].iloc[i],
                            filtered_data_batsman['3s'].iloc[i]  # Add this line
                        )
                        ax.scatter(pitch_x, pitch_y, marker='.', color=point_color)

                    ax.set_title("PitchMap of " + batsman)
                    ax.set_xticks([])
                    ax.set_yticks([])
                        
                    legend_elements = [
                        plt.Line2D([0], [0], marker='.', color='w', label='0s', markerfacecolor='black', markersize=10),
                        plt.Line2D([0], [0], marker='.', color='w', label='1s', markerfacecolor='goldenrod', markersize=10),
                        plt.Line2D([0], [0], marker='.', color='w', label='2s', markerfacecolor='blue', markersize=10),
                        plt.Line2D([0], [0], marker='.', color='w', label='3s', markerfacecolor='green', markersize=10),
                        plt.Line2D([0], [0], marker='.', color='w', label='4s', markerfacecolor='darkblue', markersize=10),
                        plt.Line2D([0], [0], marker='.', color='w', label='6s', markerfacecolor='red', markersize=10),
                        plt.Line2D([0], [0], marker='.', color='w', label='Out', markerfacecolor='azure', markersize=10),
                        ]
                    ax.legend(handles=legend_elements, loc='upper left')

                    png_filename = f"{output_dir}/{batsman}.png"
                    fig.savefig(png_filename)
                    plt.close(fig)

                    zip_file.write(png_filename, os.path.basename(png_filename))
        
        st.download_button('Download ZIP', data=zip_buffer.getvalue(), file_name='pitch_maps.zip', mime='application/zip')

# Constants for pitch map calculations
old_reg_start_y = 0
old_reg_stump_y = 101
old_reg_2m_y = 263
old_reg_4m_y = 439
old_reg_6m_y = 620
old_reg_8m_y = 808
old_reg_10m_y = 1005
old_reg_end_y = 1788
old_reg_xlen = 364

pitch_map_height = 600
pitch_map_weight = 1080
pitch_map_start_y = 153
pitch_map_stump_y = 178
pitch_map_2m_y = 208
pitch_map_4m_y = 253
pitch_map_6m_y = 298
pitch_map_8m_y = 352
pitch_map_10m_y = 408
pitch_map_end_y = 489

pitch_map_start_x1p = 344
pitch_map_start_x2p = 704
pitch_map_stump_x1p = 339
pitch_map_stump_x2p = 709
pitch_map_2m_x1p = 332
pitch_map_2m_x2p = 714
pitch_map_4m_x1p = 323
pitch_map_4m_x2p = 722
pitch_map_6m_x1p = 316 
pitch_map_6m_x2p = 729
pitch_map_8m_x1p = 306
pitch_map_8m_x2p = 742
pitch_map_10m_x1p = 294
pitch_map_10m_x2p = 752
pitch_map_end_x1p = 277
pitch_map_end_x2p = 769

if __name__ == "__main__":
    main()
