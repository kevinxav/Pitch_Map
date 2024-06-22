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

def calculate_pitch_map_coordinates(length_x, length_y, origin_x, origin_y, is_1s, is_2s, is_3s, is_4s, is_6s, is_0s, is_batwkts):
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

def filter_data_by_phase(data, phase_column, selected_phase):
    if selected_phase == "All":
        return data
    else:
        return data[data[phase_column] == selected_phase]

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

    match_ids = ['All'] + list(filtered_data['matchid'].unique())
    selected_match_id = st.multiselect("Select Match:", match_ids, default=['All'])
    
    if 'All' not in selected_match_id:
        filtered_data = filtered_data[filtered_data['matchid'].isin(selected_match_id)]
    
    # Filter batsman names based on match id
    batsman_names = ['All'] + list(filtered_data['StrikerName'].unique())
    selected_batsman_name = st.multiselect("Select the batsman's name:", batsman_names, default=['All'])
    
    if selected_batsman_name:
        # Pace or Spin filter
        pace_or_spin = st.multiselect("Select bowler type (Pace/Spin):", ["All", "Pace", "Spin"], default=["All"])
        
        if "All" not in pace_or_spin:
            pace_or_spin_values = []
            if "Pace" in pace_or_spin:
                pace_or_spin_values.append(1)
            if "Spin" in pace_or_spin:
                pace_or_spin_values.append(2)
            filtered_data = filtered_data[filtered_data['PaceorSpin'].isin(pace_or_spin_values)]
        
        # Bowling Type Group filter
        if "Pace" in pace_or_spin:
            bowling_type_options = ["All", "RAP", "LAP"]
            selected_bowling_types = st.multiselect("Select Bowling Type Group:", bowling_type_options, default=["All"])
            if "All" not in selected_bowling_types:
                bowling_type_values = []
                if "RAP" in selected_bowling_types:
                    bowling_type_values.append(1)
                if "LAP" in selected_bowling_types:
                    bowling_type_values.append(2)
                filtered_data = filtered_data[filtered_data['BowlingTypeGroup'].isin(bowling_type_values)]
        
        if "Spin" in pace_or_spin:
            bowling_type_options = ["All", "RAO", "SLAO", "RALB", "LAC"]
            selected_bowling_types = st.multiselect("Select Bowling Type Group:", bowling_type_options, default=["All"])
            if "All" not in selected_bowling_types:
                bowling_type_values = []
                if "RAO" in selected_bowling_types:
                    bowling_type_values.append(3)
                if "SLAO" in selected_bowling_types:
                    bowling_type_values.append(4)
                if "RALB" in selected_bowling_types:
                    bowling_type_values.append(5)
                if "LAC" in selected_bowling_types:
                    bowling_type_values.append(6)
                filtered_data = filtered_data[filtered_data['BowlingTypeGroup'].isin(bowling_type_values)]
        
        # Phase selection
        phase_type = st.selectbox("Select phase type (3Phase/4Phase):", ["3Phase", "4Phase"])
        if phase_type == "3Phase":
            phase_options = ["All", 1, 2, 3]
            selected_phase = st.selectbox("Select Phase:", phase_options, index=0)
            filtered_data = filter_data_by_phase(filtered_data, 'Phase3idStar', selected_phase)
        elif phase_type == "4Phase":
            phase_options = ["All", 1, 2, 3, 4]
            selected_phase = st.selectbox("Select Phase:", phase_options, index=0)
            filtered_data = filter_data_by_phase(filtered_data, 'Phase4id', selected_phase)

        run_types = st.multiselect("Select run types:", ['0s', '1s', '2s', '3s', '4s', '6s', 'wickets', 'All'], default=['All'])
        
        output_dir = 'output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for batsman_name in selected_batsman_name:
                if batsman_name == 'All':
                    batsman_data = filtered_data
                else:
                    batsman_data = filtered_data[filtered_data['StrikerName'] == batsman_name]
                
                if not batsman_data.empty:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    pitch_map_img = Image.open("pitch_map.jpg")
                    ax.imshow(pitch_map_img, extent=[0, 100, 0, 100])
                    
                    for _, row in batsman_data.iterrows():
                        length_x = row['stumpsx']
                        length_y = row['stumpsy']
                        origin_x = row['stumpsx']
                        origin_y = row['stumpsy']
                        is_1s = row['is1s']
                        is_2s = row['is2s']
                        is_3s = row['is3s']
                        is_4s = row['is4s']
                        is_6s = row['is6s']
                        is_0s = row['is0s']
                        is_batwkts = row['isbatwkts']
                        
                        x_axis, y_axis, color = calculate_pitch_map_coordinates(
                            length_x, length_y, origin_x, origin_y,
                            is_1s, is_2s, is_3s, is_4s, is_6s, is_0s, is_batwkts
                        )
                        
                        ax.scatter(x_axis, y_axis, color=color, s=10)
                    
                    ax.set_title(f"Pitch Map for {batsman_name}")
                    plt.axis('off')
                    
                    # Save the figure
                    file_path = os.path.join(output_dir, f"{batsman_name}.png")
                    plt.savefig(file_path, bbox_inches='tight')
                    plt.close(fig)
                    
                    # Add the figure to the zip file
                    zip_file.write(file_path, os.path.basename(file_path))
        
        # Save the zip file
        zip_buffer.seek(0)
        st.download_button(label="Download Pitch Maps", data=zip_buffer, file_name="pitch_maps.zip", mime="application/zip")

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
