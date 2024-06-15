import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd

def calculate_pitch_map_coordinates(length_x, length_y, origin_x, origin_y, is_1s, is_2s, is_4s, is_6s, is_0s, is_batwkts):
    x_axis = calculate_pitch_map_xaxis(length_x, length_y, origin_x)
    y_axis = calculate_pitch_map_yaxis(length_y, origin_y)
    
    if is_1s == 1:
        color = 'goldenrod'
    elif is_2s == 1:
        color = 'blue'
    elif is_4s == 1:
        color = 'darkblue'
    elif is_6s == 1:
        color = 'red'
    elif is_0s == 1:
        color = 'black'
    elif is_batwkts == 1:
        color = 'azure'
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

def main():
    st.title("Cricket Pitch Map Visualization")

    csv_path = "Ausvsnz.csv"
    data = pd.read_csv(csv_path)

    unique_striker_names = data['StrikerName'].unique()

    # Create a selectbox with the unique striker names
    selected_striker = st.selectbox('Select a Striker', unique_striker_names, key='unique_striker_selectbox')

    # Check if the selected striker is in the DataFrame and display their batting type
    if selected_striker:
        batting_type = data.loc[data['StrikerName'] == selected_striker, 'BattingType'].iloc[0]
        st.write(f'The batting type of {selected_striker} is {batting_type}')

        if batting_type == 'RHB':
            image_path = 'pitchR.jpg'
        elif batting_type == 'LHB':
            image_path = 'pitchL.jpg'
        unique_striker_names = data['StrikerName'].unique()

    # Create a selectbox with the unique striker names
    selected_striker = st.selectbox('Select a Striker', unique_striker_names)

    # Check if the selected striker is in the DataFrame and display their batting type
    if selected_striker:
        batting_type = data.loc[data['StrikerName'] == selected_striker, 'BattingType'].iloc[0]
        st.write(f'The batting type of {selected_striker} is {batting_type}')
        spin_or_pace = st.selectbox("Choose bowler type", ['Pace', 'Spin', 'Both'])

        bowler_type_mapping_pace = {'RAP': 1, 'LAP': 2, 'Both': 3}
        bowler_type_mapping_spin = {'RAO': 3, 'SLAO': 4, 'RALB': 5, 'LAC': 6, 'All': 7}

        overs_phase = st.selectbox("Choose overs phase", ['Power Play (1-6)', 'Middle Overs (7-15)', 'Death Overs (16-20)', 'All'])

        specific_runs = st.selectbox("Choose specific runs", ['0s', '1s', '2s', '3s', '4s', '6s', 'batwkts', 'all'])

        if st.button("Apply Filter"):
            if spin_or_pace == 'Pace':
                pace_type = st.selectbox("Choose pace type", list(bowler_type_mapping_pace.keys()))
                filtered_data = data[(data['StrikerName'] == batsman_name) & (data['PaceOrSpin'] == 1) & (data['BowlerType'] == bowler_type_mapping_pace[pace_type])]
            elif spin_or_pace == 'Spin':
                spin_type = st.selectbox("Choose spin type", list(bowler_type_mapping_spin.keys()))
                if spin_type == 'All':
                    filtered_data = data[(data['StrikerName'] == batsman_name) & (data['PaceOrSpin'] == 2)]
                else:
                    filtered_data = data[(data['StrikerName'] == batsman_name) & (data['PaceOrSpin'] == 2) & (data['BowlerType'] == bowler_type_mapping_spin[spin_type])]
            else:
                filtered_data = data[data['StrikerName'] == batsman_name]

            filtered_data = filter_data_by_overs(filtered_data, overs_phase)

            if specific_runs != 'all':
                filtered_data = filtered_data[filtered_data[specific_runs] == 1]

            if not filtered_data.empty:
                img = Image.open(image_path)
                img_array = plt.imread(image_path)
                height, width, _ = img_array.shape
                origin_x, origin_y = 0, 0

                fig, ax = plt.subplots()
                ax.imshow(img_array, extent=[0, width, 0, height])

                for i in range(len(filtered_data)):
                    pitch_x, pitch_y, point_color = calculate_pitch_map_coordinates(filtered_data['X'].iloc[i], filtered_data['Y'].iloc[i], origin_x, origin_y, 
                                                                        filtered_data['1s'].iloc[i], filtered_data['2s'].iloc[i], filtered_data['4s'].iloc[i], filtered_data['6s'].iloc[i],
                                                                        filtered_data['0s'].iloc[i], filtered_data['batwkts'].iloc[i])
                    ax.scatter(pitch_x, pitch_y, marker='.', color=point_color)

                ax.set_title("PitchMap of " + batsman_name)
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
                ax.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.48, 0.05), ncol=7, prop={'size':8})
                
                st.pyplot(fig)
            else:
                st.write("No data found for the selected filters.")
    else:
        st.write(f"Batsman with name '{batsman_name}' not found in the data.")

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
