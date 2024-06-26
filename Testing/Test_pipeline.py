import time
import datetime
import numpy as np
import pandas as pd
from tqdm import tqdm
import math
import importlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import re
import seaborn as sns

time_options = ['0,01', '0,1', '0,5', '1', '5', '10']
excel_df = pd.DataFrame(columns=time_options)



for z in time_options:
    selected_time = z # THIS IS THE ONE THAT SELECTS THE TIME INTERVAL FOR ALL THE MODELS DOWN UNDER!!!!! time_options = ['0,01', '0,1', '0,5', '1', '5', '10']

    time_dict = {'0,01': '10L', '0,1': '100L', '0,5': '500L', '1': '1S', '5': '5S', '10': '10S'}
    standardized_dict = {'0,01': 25, '0,1': 2.5, '0,5': 1/2, '1': 1/4, '5': 1/20, '10': 1/40}

    #import the csv file
    label_df_new = pd.read_csv(f'/Users/jensknudsen/Desktop/result/{selected_time}/predictions_depth5_time{time_dict[selected_time]}_window5_predicted.csv')

    val_procent = 0.2

    # Calculate the number of samples that should be in the training set
    num_samples = len(label_df_new) * val_procent


    def closest_value(input):
        # Adjust the input to the closest higher multiple of 250
        return int(input + (200 - input % 200))

    train_samples = closest_value(num_samples)


    val_df= label_df_new[:train_samples]
    test_df = label_df_new[train_samples:]

    print(len(val_df))
    print(len(test_df))
    print(len(test_df)+len(val_df))

    # for the column selected_time in the excel_df add the rows: len(val_df)
    excel_df.loc['Lenght of validation data', selected_time] = len(val_df)

    excel_df.loc['Lenght of test data', selected_time] = len(test_df)

    excel_df.loc['Lenght of all test dataset', selected_time] = len(test_df)+len(val_df)
    print('good')
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    # Reset matplotlib to default settings
    mpl.rcParams.update(mpl.rcParamsDefault)

    # If you've previously used Seaborn and want to ensure it's reset, you can also do:
    plt.style.use('default')


    pd.options.display.float_format = '{:.6}'.format
    import pandas as pd


    # Create an empty DataFrame to store the results
    decile_means = pd.DataFrame()

    # Group by 'Time' and process each group
    for time, group in test_df.groupby('Time'):

        # Assign deciles based on 'predicted_return'
        # 'labels=False' gives integer codes from 0 to 9 instead of interval categories
        group['Decile'] = pd.qcut(group['predicted_return'], 10, labels=False, duplicates='drop')

        # Calculate the mean 'midquote' for each decile
        decile_mean = group.groupby('Decile')['midquote'].mean().reset_index()
        decile_mean['Time'] = time  # Add the time for tracking

        # Append the results to the decile_means DataFrame
        decile_means = pd.concat([decile_means, decile_mean], ignore_index=True)

    # Pivot the DataFrame to have Time as index, Deciles as columns, and mean midquotes as values
    decile_means_pivot = decile_means.pivot(index='Time', columns='Decile', values='midquote')

    #for nan values replace with 0
    decile_means_pivot = decile_means_pivot.fillna(0)

    # make this to a dataframe: decile_means_pivot.mean(axis=0)
    returns_for_decile = decile_means_pivot.mean(axis=0)

    #for each column calculate the sharpe ratio
    import numpy as np

    # Assuming decile_means_pivot is prepared as before

    # Calculate the Sharpe ratio for each decile
    sharpe_ratios = decile_means_pivot.mean(axis=0) / decile_means_pivot.std(axis=0)
    sharpe_ratios

    # combine returns_for_decile and sharpe_ratios to a dataframe
    returns_for_decile = returns_for_decile.to_frame()
    returns_for_decile['sharpe_ratios'] = sharpe_ratios
    # rename the columns 
    returns_for_decile.columns = ['returns', 'sharpe_ratios']
    returns_for_decile
    
    
    # Assuming returns_for_decile is already defined and contains 'returns' and 'sharpe_ratios' for each decile
    # Sample data for demonstration
    deciles = np.arange(1, 11)  # Deciles 1 through 10
    
    
    # Plotting
    fig, ax1 = plt.subplots(figsize=(20, 10))
    
    color_for_returns = 'tab:blue' # dark blue color
    color_for_sharpe = 'tab:red'
    
    # Bar plot for returns
    ax1.bar(deciles, returns_for_decile['returns'], color=color_for_returns, alpha=0.6, label='Return')
    ax1.set_ylabel('Return', color=color_for_returns, fontsize=16)
    ax1.tick_params(axis='y', labelcolor=color_for_returns, labelsize=14)
    ax1.set_xticks(deciles)  # Ensure we have ticks for each decile
    # Explicitly setting the x-tick labels to correspond to each decile
    ax1.set_xticklabels([f'Decile {d}' for d in deciles], rotation=45, fontsize=16)
    
    
    # Secondary y-axis for Sharpe ratios
    ax2 = ax1.twinx()
    ax2.plot(deciles, returns_for_decile['sharpe_ratios'], color=color_for_sharpe, marker='o', linestyle='--', linewidth=2, markersize=8, label='Sharpe Ratios')
    ax2.set_ylabel('Sharpe Ratio', color=color_for_sharpe, fontsize=16)
    ax2.tick_params(axis='y', labelcolor=color_for_sharpe, labelsize=14)
    
    # Adding combined legend for both plots
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left', fontsize=20)
    
    plt.tight_layout()
    #plt.title(f"Returns and Sharpe Ratios by Decile for {selected_time} Seconds", fontsize=16)
    plt.tight_layout()  # Adjust layout
    #plt.show()


    # for the returns_for_decile add a new row that name is H-L and calculate the difference between decile 9 and decile 0 for the returns column
    returns_for_decile.loc['H-L'] = returns_for_decile.loc[9] - returns_for_decile.loc[0]

    pd.options.display.float_format = '{:.7f}'.format
    import pandas as pd
    #for each time in decile_means_pivot add the decile 0 and 9 to a new column:
    decile_means_pivot['decile_0'] = decile_means_pivot[0]
    decile_means_pivot['decile_9'] = decile_means_pivot[9]

    # for each time in decile_means_pivot calculate the difference between decile 9 and decile 0 and add it to a new column:
    decile_means_pivot['difference'] = (decile_means_pivot['decile_9'] - decile_means_pivot['decile_0'])

    SR_H_L = decile_means_pivot['difference'].mean(axis=0) / decile_means_pivot['difference'].std(axis=0)

    #for the H-L row for the sharpe_ratios only coloumn insert the SR_H_L:

    returns_for_decile.loc['H-L', 'sharpe_ratios'] = SR_H_L

    # make a new column that is the standardize sharpe ratio

    returns_for_decile['standardized_sharpe_ratios'] = returns_for_decile['sharpe_ratios'] * math.sqrt(standardized_dict[selected_time])

    #rename the columns
    returns_for_decile.columns = ['Ret', 'SR', 'Std. SR (1 sec)']

    # Convert the DataFrame to LaTeX code
    formatters = {
        'Ret': '{:0.7f}'.format,  # No decimal places for integer column
        'SR': '{:0.3f}'.format,  # Two decimal places for the first float column
        'Std. SR (1 sec)': '{:0.3f}'.format  # Four decimal places for the second float column
    }

    latex_code = returns_for_decile.to_latex(caption=f"For the {selected_time} Second Model", label=f"tab:{selected_time} Second Model for return, SR and Std. SR", formatters=formatters)

    print(latex_code)

    # Save the LaTeX code to a file
    with open(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/returns_for_decile_{time_dict[selected_time]}.tex', 'w') as f:
        f.write(latex_code)

    # save the picture to a file
    fig.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/table_for_decile_{time_dict[selected_time]}.png')


    # This is for the direction of the best predictions
    displayit = label_df_new.sort_values(by='predicted_return', ascending=False).iloc[0:250]

    # make a list of the filenames for the displayit
    displayit_list = displayit['Filename'].tolist()

    # reset index for displayit
    displayit = displayit.reset_index(drop=False)

    # delete the unnamed: 0 column
    displayit = displayit.drop(columns=['Unnamed: 0'])

    displayit['index'] = displayit.index

    # Apply the default Seaborn theme with some enhancements
    sns.set_theme(style="whitegrid")

    # Sort the data by 'predicted_return' in descending order for correct visualization
    displayit = displayit.sort_values(by='predicted_return', ascending=False)

    # Create a unique identifier for each row to handle duplicates in 'predicted_return'
    displayit['unique_predicted_return'] = displayit['predicted_return'].astype(str) + '_' + displayit.groupby('predicted_return').cumcount().astype(str)

    # Create a figure and axis with a specified size
    fig, ax = plt.subplots(figsize=(20, 10))

    # Define colors based on 'midquote' values
    colors = ['green' if x > 0 else 'red' for x in displayit['midquote']]

    # Use Seaborn's barplot to plot the data with 'unique_predicted_return' as x and 'midquote' as y
    # Use the defined colors for each bar
    barplot = sns.barplot(data=displayit, x='unique_predicted_return', y='midquote', ax=ax, palette=colors)

    # Adding labels and title with improved font sizes
    ax.set_xlabel('Target Value Prediction', fontsize=14)
    ax.set_ylabel('Real Return', fontsize=14)

    # Customize x-axis tick labels to show only the first four characters of each ticker
    ax.set_xticklabels([label.split('_')[0][:5] for label in displayit['unique_predicted_return']])

    # Rotate x-axis labels to avoid overlap and improve readability display only the 2 decimals
    #plt.xticks(rotation=90, size=10)

    # Customize x-axis tick labels to show only every 5th label
    plt.xticks(ticks=ax.get_xticks()[::5], labels=[label.get_text() for label in ax.get_xticklabels()[::5]], rotation=90, size=10)


    # Add small yellow horizontal lines at the zero line for bars where 'midquote' is zero
    for i, p in enumerate(barplot.patches):
        # Check if the corresponding 'midquote' value is zero
        if displayit.iloc[i]['midquote'] == 0:
            # Draw a small horizontal yellow line at the zero position
            ax.hlines(0, p.get_x(), p.get_x() + p.get_width(), colors='yellow', lw=3)  # Adjust linewidth as needed

    # save the picture to a file
    fig.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/prediction_direction_for_best_long_{time_dict[selected_time]}.png')

    # display the columns with the highest predicted_return
    displayit = label_df_new.sort_values(by='predicted_return', ascending=True).iloc[0:250]
    # display the first Arrays in displayit
    #ds= displayit['Filename'].iloc[0]

    # make a list of the filenames for the displayit
    displayit_list = displayit['Filename'].tolist()

    #displayit = displayit.sort_values(by='midquote', ascending=False)
    # reset index for displayit
    displayit = displayit.reset_index(drop=False)

    # delete the unnamed: 0 column
    displayit = displayit.drop(columns=['Unnamed: 0'])


    displayit['index'] = displayit.index

    # Apply the default Seaborn theme with some enhancements
    sns.set_theme(style="whitegrid")
    
    
    # Create a unique identifier for each row to handle duplicates in 'predicted_return'
    displayit['unique_predicted_return'] = displayit['predicted_return'].astype(str) + '_' + displayit.groupby('predicted_return').cumcount().astype(str)
    
    # Create a figure and axis with a specified size
    fig, ax = plt.subplots(figsize=(20, 10))
    
    # Define colors based on 'midquote' values
    colors = ['green' if x > 0 else 'red' for x in displayit['midquote']]
    
    # Use Seaborn's barplot to plot the data with 'unique_predicted_return' as x and 'midquote' as y
    # Use the defined colors for each bar
    barplot = sns.barplot(data=displayit, x='unique_predicted_return', y='midquote', ax=ax, palette=colors)
    
    # Adding labels and title with improved font sizes
    ax.set_xlabel('Target Value Prediction', fontsize=14)
    ax.set_ylabel('Real Return', fontsize=14)
    
    # Customize x-axis tick labels to show only the first four characters of each ticker
    ax.set_xticklabels([label.split('_')[0][:5] for label in displayit['unique_predicted_return']])
    
    # Rotate x-axis labels to avoid overlap and improve readability display only the 2 decimals
    plt.xticks(ticks=ax.get_xticks()[::5], labels=[label.get_text() for label in ax.get_xticklabels()[::5]], rotation=90, size=10)
    
    # Add small yellow horizontal lines at the zero line for bars where 'midquote' is zero
    for i, p in enumerate(barplot.patches):
        # Check if the corresponding 'midquote' value is zero
        if displayit.iloc[i]['midquote'] == 0:
            # Draw a small horizontal yellow line at the zero position
            ax.hlines(0, p.get_x(), p.get_x() + p.get_width(), colors='yellow', lw=3)  # Adjust linewidth as needed
    
    fig.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/prediction_direction_for_best_short_{time_dict[selected_time]}.png')
    

    def calculate_combined_for_best(x, y, df):
        pd.options.display.float_format = '{:.7f}'.format

        high_conf_pos = df[df['predicted_return'] > x]
        high_conf_neg = df[df['predicted_return'] < y]

        # make a list to store both time and midquote values
        list_positive = high_conf_pos['midquote'].tolist()
        list_for_time_positive = high_conf_pos['Time'].tolist()

        # combine the two lists list_positive and list_for_time_positive to a dataframe
        Combineit_pos = pd.DataFrame(list_positive, list_for_time_positive)
        # sort after the time

        list_negative = high_conf_neg['midquote'].tolist()
        list_negative = [-x for x in list_negative] # for the short strategy (convert the value with negative value)
        list_for_time_negative = high_conf_neg['Time'].tolist()


        Combineit_neg = pd.DataFrame(list_negative, list_for_time_negative)

        # make the index a column
        Combineit_pos.reset_index(inplace=True)
        Combineit_neg.reset_index(inplace=True)

        # rename the columns
        if len(Combineit_pos)>0:
            Combineit_pos.columns = ['time', 'midquote']
            Combineit_pos = Combineit_pos.groupby('time').mean()
        else:
            Combineit_pos = pd.DataFrame(columns=['time', 'midquote'])


        if len(Combineit_neg)>0:
            Combineit_neg.columns = ['time', 'midquote']
            Combineit_neg = Combineit_neg.groupby('time').mean()
        else:
            Combineit_neg= pd.DataFrame(columns=['time', 'midquote'])


        if len(Combineit_neg)>0:
            if len(Combineit_pos>0):
                Combineit = Combineit_pos.merge(Combineit_neg, on='time', how='outer')
                Combineit.columns = ['midquote_positive', 'midquote_negative']

                count_positive = high_conf_pos['Time'].value_counts()
                count_negative = high_conf_neg['Time'].value_counts()

                Combineit = Combineit.merge(count_positive, left_on='time', right_on=count_positive.index, how='outer')
                Combineit = Combineit.merge(count_negative, left_on='time', right_on=count_negative.index, how='outer')

                Combineit.columns = ['time', 'return_positive', 'return_negative', 'count_positive', 'count_negative']
                # for nan values replace with 0
                Combineit['return_positive'] = Combineit['return_positive'].fillna(0)
                Combineit['return_negative'] = Combineit['return_negative'].fillna(0)
                Combineit['count_positive'] = Combineit['count_positive'].fillna(0)
                Combineit['count_negative'] = Combineit['count_negative'].fillna(0)

                Combineit['combined_return'] = (Combineit['return_positive'] * Combineit['count_positive'] / (Combineit['count_positive'] + Combineit['count_negative'])) + (Combineit['return_negative'] * Combineit['count_negative'] / (Combineit['count_positive'] + Combineit['count_negative']))



        if len(Combineit_neg)==0:
            Combineit = Combineit_pos
            Combineit.columns = ['midquote_positive']
            count_positive = high_conf_pos['Time'].value_counts()
            Combineit = Combineit.merge(count_positive, left_on='time', right_on=count_positive.index, how='outer')
            Combineit.columns = ['time', 'return_positive', 'count_positive']
            Combineit['return_positive'] = Combineit['return_positive'].fillna(0)
            Combineit['count_positive'] = Combineit['count_positive'].fillna(0)
            Combineit['combined_return'] = Combineit['return_positive']

        if len(Combineit_pos)==0:
            Combineit = Combineit_neg
            Combineit.columns = ['midquote_negative']
            count_negative = high_conf_neg['Time'].value_counts()
            Combineit = Combineit.merge(count_negative, left_on='time', right_on=count_negative.index, how='outer')
            Combineit.columns = ['time', 'return_negative', 'count_negative']
            Combineit['return_negative'] = Combineit['return_negative'].fillna(0)
            Combineit['count_negative'] = Combineit['count_negative'].fillna(0)
            Combineit['combined_return'] = Combineit['return_negative']


        combined_for_best = Combineit['combined_return'].mean()/Combineit['combined_return'].std()

        return(combined_for_best)

    def calculate_positive_for_best(x, df):
        pd.options.display.float_format = '{:.7f}'.format

        high_conf_pos = df[df['predicted_return'] > x]

        # make a list to store both time and midquote values
        list_positive = high_conf_pos['midquote'].tolist()
        list_for_time_positive = high_conf_pos['Time'].tolist()

        # combine the two lists list_positive and list_for_time_positive to a dataframe
        Combineit_pos = pd.DataFrame(list_positive)
        # sort after the time

        # make the index a column
        Combineit_pos.reset_index(inplace=True)

        # rename the columns
        if len(Combineit_pos)>0:
            Combineit_pos.columns = ['time', 'midquote']
            Combineit_pos = Combineit_pos.groupby('time').mean()
        else:
            Combineit_pos = pd.DataFrame(columns=['time', 'midquote'])

        Combineit_pos.columns = ['midquote_positive']
        positive_for_best = Combineit_pos['midquote_positive'].mean()/Combineit_pos['midquote_positive'].std()

        return(positive_for_best)

    def calculate_negative_for_best(y, df):
        pd.options.display.float_format = '{:.7f}'.format


        high_conf_neg = df[df['predicted_return'] < y]

        # sort after the time

        list_negative = high_conf_neg['midquote'].tolist()
        list_negative = [-x for x in list_negative] # for the short strategy (convert the value with negative value)
        list_for_time_negative = high_conf_neg['Time'].tolist()


        Combineit_neg = pd.DataFrame(list_negative, list_for_time_negative)
        # make the index a column
        Combineit_neg.reset_index(inplace=True)


        if len(Combineit_neg)>0:
            Combineit_neg.columns = ['time', 'midquote']
            Combineit_neg = Combineit_neg.groupby('time').mean()
        else:
            Combineit_neg= pd.DataFrame(columns=['time', 'midquote'])

        Combineit_neg.columns = ['midquote_negative']
        negative_for_best = Combineit_neg['midquote_negative'].mean()/Combineit_neg['midquote_negative'].std()

        return(negative_for_best)


    import numpy as np
    import matplotlib.pyplot as plt

    # Assuming the calculate_positive_for_best function and val_df are defined elsewhere

    # Setup for grid search
    best_sharpe_ratio_positive = -np.inf
    best_x_positive = 0  # Corrected variable name for consistency

    # Define the range of x values
    # Assuming you are interested in optimizing within a specific range of predicted returns

    # Calculate the number of rows that represent 1% of the DataFrame's total rows
    w = 0.5 # in procent  
    percent_count = int(len(val_df) * (w/100))

    max_val = val_df['predicted_return'].nlargest(percent_count).iloc[-1]
    x_values = np.linspace(0.50, max_val, num=2000, endpoint=False)

    # Initialize an array to store Sharpe ratios for visualization
    sharpe_ratios = np.zeros(len(x_values))

    # Perform grid search over x values
    for i, x in enumerate(x_values):
        sharpe_ratio = calculate_positive_for_best(x, val_df)
        sharpe_ratios[i] = sharpe_ratio

        # Check for new best Sharpe ratio
        if sharpe_ratio > best_sharpe_ratio_positive:
            best_sharpe_ratio_positive = sharpe_ratio
            best_x_positive = x

    # Print the best Sharpe Ratio and corresponding x value
    print(f"Best Sharpe Ratio: {best_sharpe_ratio_positive:.4f}, Best x: {best_x_positive:.4f}")

    # Plotting
    plt.figure(figsize=(14, 7))

    # Plot all the Sharpe ratios as a line
    plt.plot(x_values, sharpe_ratios, linestyle='-', label='Sharpe Ratio')

    # Highlight the point with the best Sharpe ratio using a marker
    plt.plot(best_x_positive, best_sharpe_ratio_positive, 'o', color='red', label='Best Sharpe Ratio')

    #plt.title(f'Validation of the Optimal Threshold to Maximize Sharpe Ratio for the Long Position for {selected_time} Seconds', fontsize=14)
    plt.xlabel('Threshold', fontsize=14)
    plt.ylabel('Sharpe Ratio', fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(True)
    plt.legend(fontsize=12)
      # save the picture to a file
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/validation_long_sharpe_ratio_optimal_{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')
    #plt.show()


    # save the best_sharpe_ratio_positive and best_x_positive to the excel_df
    excel_df.loc['Best Sharpe Ratio for validation for long', selected_time] = best_sharpe_ratio_positive
    excel_df.loc['Best threshold for validation for long', selected_time] = best_x_positive

    # make a print statement that calculates the sharpe ratio based on the optimal threshold for the long position in the test dataset
    print(f"Sharpe ratio based on the optimal threshold for the long position in the test dataset: {calculate_positive_for_best(best_x_positive, test_df):.8f}")

    # save the best sharpe ratio based on the test dataset to the excel_df
    excel_df.loc['Best Sharpe Ratio for test data for long', selected_time] = calculate_positive_for_best(best_x_positive, test_df)

    import pandas as pd

    # Creating a copy of the filtered DataFrame to avoid SettingWithCopyWarning
    high_conf_pos = test_df[test_df['predicted_return'] > best_x_positive].copy()

    # Now you can safely modify high_conf_pos without worrying about affecting test_df
    high_conf_pos['correct_prediction'] = ((high_conf_pos['predicted_return'] >= 0.5) & (high_conf_pos['midquote_target'] >= 0.5)) | ((high_conf_pos['predicted_return'] < 0.5) & (high_conf_pos['midquote_target'] < 0.5))

    # Calculate and print the overall accuracy
    overall_accuracy = high_conf_pos['correct_prediction'].mean()
    print(f"Overall Accuracy Score: {overall_accuracy:.6f}")


    # save the overall accuracy to the excel_df
    excel_df.loc['Overall accuracy for test data for long after optimal threshold', selected_time] = overall_accuracy

    import seaborn as sns
    import matplotlib.pyplot as plt

    # make a dictionary that contains the different x-axis values for the different time intervals
    x_dict = {'0,01': '%H:%M:%S', '0,1': '%H:%M:%S', '0,5': '%H:%M', '1': '%H:%M', '5': '%H:%M', '10': '%H:%M'}

    # Assuming high_conf_pos and selected_time are already defined

    # Group data by 'Time' and 'correct_prediction' to count occurrences
    prediction_counts = high_conf_pos.groupby(['Time', 'correct_prediction']).size().unstack(fill_value=0)

    prediction_counts.columns = prediction_counts.columns.map({True: 'Correct Prediction', False: 'Incorrect Prediction'})

    # Reset index to make 'Time' a column again (useful for seaborn plotting)
    prediction_counts.reset_index(inplace=True)
    # Convert the Time column to datetime
    prediction_counts['Time'] = pd.to_datetime(prediction_counts['Time'])

    #Create a date range from the first to the last timestamp with 1-second intervals
    date_range = pd.date_range(start=prediction_counts['Time'].min(), end=prediction_counts['Time'].max(), freq=time_dict[selected_time])

    prediction_counts.set_index('Time', inplace=True)
    prediction_counts_complete = prediction_counts.reindex(date_range, fill_value=0).reset_index()
    prediction_counts_complete.rename(columns={'index': 'Time'}, inplace=True)

    # make a momving average for the prediction_counts_complete for the incorrect prediction and the correct prediction columns
    prediction_counts_complete['correct_prediction_moving_average'] = prediction_counts_complete['Correct Prediction'].rolling(window=200).mean()
    prediction_counts_complete['incorrect_prediction_moving_average'] = prediction_counts_complete['Incorrect Prediction'].rolling(window=200).mean()

    prediction_counts_complete['sum_of_the_two'] = prediction_counts_complete['Correct Prediction'] + prediction_counts_complete['Incorrect Prediction']
    # remove the first 200 rows 
    prediction_counts_complete = prediction_counts_complete[200:]

    # Set the overall aesthetics
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(12, 9))

    # Plot the upper portion (4/5 of the upper half)
    ax1 = plt.subplot(2, 1, 1)
    sns.lineplot(data=prediction_counts_complete, x='Time', y='correct_prediction_moving_average', label='Correct Predictions (MA)', color='seagreen', ax=ax1)
    sns.lineplot(data=prediction_counts_complete, x='Time', y='incorrect_prediction_moving_average', label='Incorrect Predictions (MA)', color='salmon', ax=ax1)

    ax1.set_ylabel('Number of Trades (MA=200)', fontsize=16)
    ax1.tick_params(axis='both', which='major', labelsize=14)
    ax1.legend(loc='upper left', fontsize=14, title='Prediction Types')
    # delete the x axis label
    ax1.set_xlabel('')
    # delete the x axis ticks
    #ax1.set_xticks([])
    # make the vertical grid lines
    # for the x-axis only display the hour and minute
    ax1.xaxis.set_major_formatter(mdates.DateFormatter(str(x_dict[selected_time])))
    ax1.grid(True, linestyle='--', linewidth=0.5)  # lighter grid lines

    ax2 = plt.subplot(2, 1, 2)

    # Assuming prediction_counts_complete DataFrame is available
    sns.histplot(data=prediction_counts_complete, x='Time', weights='sum_of_the_two', bins=len(prediction_counts_complete), color='dimgray')
    ax2.set_xlabel('Time', fontsize=14)
    ax2.set_ylabel('Sum of Predictions', fontsize=16)
    ax2.tick_params(axis='both', which='major', labelsize=14)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter(str(x_dict[selected_time])))
    ax2.grid(True, linestyle='--', linewidth=0.5)  # lighter grid lines

    plt.tight_layout()

    # save the picture to a file
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/accuracy_over_time_long_{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')

    #plt.show()


    import matplotlib.pyplot as plt
    import numpy as np

    # Assuming `high_conf_pos`, `test_df`, `best_x_positive`, and `selected_time` are defined

    tickers_counts = high_conf_pos['Ticker'].value_counts().sort_values(ascending=False)

    # Calculate correct and incorrect counts based on 'correct_prediction' column
    correct_counts = high_conf_pos[high_conf_pos['correct_prediction'] == 1]['Ticker'].value_counts()
    incorrect_counts = high_conf_pos[high_conf_pos['correct_prediction'] == 0]['Ticker'].value_counts()

    # Assuming the second method is the one we're using for average spread
    average_spread_per_ticker = high_conf_pos.groupby('Ticker')['spread'].mean()
    average_spread_per_ticker = average_spread_per_ticker.round(2)

    # Making the figure and primary axis for the bar chart
    fig, ax1 = plt.subplots(figsize=(20, 10))

    # Plotting the correct and incorrect ticker counts as stacked bars
    ax1.bar(tickers_counts.index, correct_counts.reindex(tickers_counts.index, fill_value=0), color='green', label='Correct Predictions')
    ax1.bar(tickers_counts.index, incorrect_counts.reindex(tickers_counts.index, fill_value=0), bottom=correct_counts.reindex(tickers_counts.index, fill_value=0), color='red', label='Incorrect Predictions')
    ax1.set_xticks(range(len(tickers_counts)))
    ax1.set_xticklabels(tickers_counts.index, fontsize=8, rotation=90)
    ax1.set_ylabel('Number of Predictions', color='black', fontsize=18)
    ax1.tick_params(axis='y', labelcolor='black', labelsize=16)

    # Creating a secondary y-axis for the average spreads
    ax2 = ax1.twinx()

    # Prepare the data for the scatter plot
    x_values = np.arange(len(tickers_counts))
    y_values = np.array([average_spread_per_ticker.get(ticker, np.nan) for ticker in tickers_counts.index])

    # Plotting the average spreads as red dots on the secondary y-axis
    ax2.scatter(x_values, y_values, color='black', label='Average Spread (AS)')
    ax2.set_ylabel('Average Spread', color='black', fontsize=18)
    ax2.tick_params(axis='y', labelcolor='black', labelsize=16)

    # Calculate and plot the line of best fit for the red dots
    z = np.polyfit(x_values, y_values, 1)
    p = np.poly1d(z)
    ax2.plot(x_values, p(x_values), color='black', linestyle='--', label='Line of Best Fit for AS')  # Specifying color and line style separately


    # Adding legends
    ax1.legend(loc='upper left', fontsize=18)
    ax2.legend(loc='upper right', fontsize=18)

    ax2.grid(False)
    ax1.grid(False)

    ax1.set_xlim(left=-0.5, right=len(tickers_counts)-0.5)

    fig.tight_layout()

    # Setting the title with a specific fontsize
    #plt.title(f'Traded Stocks for Long Strategy with Optimal Threshold of {best_x_positive:.4f} for the {selected_time} Second Model', fontsize=20)

    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/traded_stocks_long_average_spread_and_ticker_count_{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')
    #plt.show()

    # calculate the mean return for each ticker
    mean_return_per_ticker = high_conf_pos.groupby('Ticker')['midquote'].mean()
    # and sort this
    mean_return_per_ticker = mean_return_per_ticker.sort_values(ascending=False)

    # can you calculate this based on the following categories:
    tickers = [
        'AAPL', 'ABBV', 'ABNB', 'ABT', 'ACN', 'ADBE', 'ADI', 'ADP', 'ADSK', 'AFL', 'AIG', 'AJG', 'AMAT', 'AMD', 'AMGN', 'AMT', 'AMX', 'AMZN', 'ANET', 'AON', 'APD', 'APH', 'APO', 'ARM', 'ASML', 'AVGO', 'AXP', 'AZN', 'AZO', 'BA', 'BABA', 'BAC', 'BBVA', 'BDX', 'BHP', 'BKNG', 'BLK', 'BMO', 'BMY', 'BN', 'BNS', 'BP', 'BRK.B', 'BSX', 'BTI', 'BUD', 'BX', 'C', 'CAT', 'CB', 'CDNS', 'CHTR', 'CI', 'CL', 'CMCSA', 'CME', 'CMG', 'CNI', 'CNQ', 'COF', 'COP', 'COST', 'CP', 'CRH', 'CRM', 'CRWD', 'CSCO', 'CSX', 'CTAS', 'CVS', 'CVX', 'DE', 'DELL', 'DEO', 'DHI', 'DHR', 'DIS', 'DUK', 'E', 'ECL', 'EL', 'ELV', 'EMR', 'ENB', 'EOG', 'EPD', 'EQIX', 'EQNR', 'ET', 'ETN', 'EW', 'FCX', 'FDX', 'FI', 'FMX', 'FTNT', 'GD', 'GE', 'GILD', 'GM', 'GOOGL', 'GS', 'GSK', 'HCA', 'HD', 'HDB', 'HLT', 'HMC', 'HON', 'HSBC', 'IBM', 'IBN', 'ICE', 'INFY', 'ING', 'INTC', 'INTU', 'ISRG', 'ITUB', 'ITW', 'JNJ', 'JPM', 'KKR', 'KLAC', 'KO', 'LIN', 'LLY', 'LMT', 'LOW', 'LRCX', 'LULU', 'MA', 'MAR', 'MCD', 'MCK', 'MCO', 'MDLZ', 'MDT', 'MELI', 'MET', 'META', 'MMC', 'MMM', 'MNST', 'MO', 'MPC', 'MRK', 'MRVL', 'MS', 'MSCI', 'MSFT', 'MSI', 'MU', 'MUFG', 'NEE', 'NFLX', 'NGG', 'NKE', 'NOC', 'NOW', 'NSC', 'NTES', 'NVDA', 'NVO', 'NVS', 'NXPI', 'ORCL', 'ORLY', 'OXY', 'PANW', 'PBR', 'PBR.A', 'PCAR', 'PDD', 'PEP', 'PFE', 'PG', 'PGR', 'PH', 'PLD', 'PM', 'PNC', 'PSA', 'PSX', 'PXD', 'PYPL', 'QCOM', 'RACE', 'REGN', 'RELX', 'RIO', 'ROP', 'ROST', 'RSG', 'RTX', 'RY', 'SAN', 'SAP', 'SBUX', 'SCCO', 'SCHW', 'SHEL', 'SHOP', 'SHW', 'SLB', 'SMFG', 'SNOW', 'SNPS', 'SNY', 'SO', 'SONY', 'SPGI', 'STLA', 'SYK', 'T', 'TD', 'TDG', 'TEAM', 'TFC', 'TGT', 'TJX', 'TM', 'TMO', 'TMUS', 'TRI', 'TRV', 'TSLA', 'TSM', 'TT', 'TTE', 'TXN', 'UBER', 'UBS', 'UL', 'UNH', 'UNP', 'UPS', 'USB', 'V', 'VALE', 'VLO', 'VRTX', 'VZ', 'WDAY', 'WELL', 'WFC', 'WM', 'WMT', 'XOM', 'ZTS'
    ]

    branches = {
        'Technology': ['AAPL', 'ADBE', 'ADI', 'ADSK', 'AMAT', 'AMD', 'AMZN', 'ASML', 'AVGO', 'CRM', 'CDNS', 'CSCO', 'CTAS', 'EA', 'IBM', 'INTC', 'INTU', 'MSFT', 'MU', 'NVDA', 'ORCL', 'PANW', 'SHOP', 'SNPS', 'TSM', 'TXN'],
        'Healthcare': ['ABBV', 'ABT', 'AON', 'AZN', 'BDX', 'BIIB', 'BMY', 'BSX', 'CI', 'CVS', 'DHR', 'GILD', 'HCA', 'JNJ', 'LLY', 'MDT', 'MRK', 'PFE', 'REGN', 'SNY', 'SYK', 'UNH', 'VRTX'],
        'Financial Services': ['AIG', 'AXP', 'BAC', 'BKNG', 'BLK', 'BRK.B', 'C', 'CME', 'COF', 'GS', 'ICE', 'JPM', 'MA', 'MCO', 'MMC', 'MS', 'PNC', 'SCHW', 'SPGI', 'TFC', 'V', 'WFC'],
        'Consumer Goods': ['EL', 'GM', 'HD', 'KO', 'LULU', 'MAR', 'MDLZ', 'NKE', 'PG', 'PM', 'PEP', 'RACE', 'RIO', 'RL', 'SBUX', 'TGT', 'TM', 'UL', 'UN', 'VLO', 'WMT'],
        'Energy': ['APA', 'BP', 'COP', 'CVX', 'E', 'ENB', 'EOG', 'EQNR', 'EPD', 'HES', 'KMI', 'MRO', 'MPC', 'OXY', 'PBR', 'PSX', 'RDS.A', 'RDS.B', 'SU', 'VLO', 'XOM'],
        'Industrial': ['BA', 'CAT', 'DE', 'EMR', 'GE', 'HON', 'LMT', 'MMM', 'NOC', 'RTX', 'UPS'],
        'Retail': ['AMZN', 'BABA', 'COST', 'JD'],
        'Telecommunication': ['CHTR', 'CMCSA', 'TMUS', 'T', 'VZ'],
        'Automotive': ['F', 'GM', 'HMC', 'TSLA', 'TM'],
        'Entertainment': ['DIS', 'NFLX', 'SNE'],
        'Agriculture': ['ADM', 'BHP', 'CNI', 'CP', 'FMC', 'MOS', 'NTR'],
        'Utilities': ['AEP', 'DUK', 'EXC', 'NEE', 'SO'],
        'Pharmaceuticals': ['ABBV', 'AZN', 'BMY', 'GILD', 'JNJ', 'MRK', 'PFE', 'SNY'],
        'Insurance': ['AIG', 'AON', 'BRK.B', 'MET', 'PRU', 'TRV']
    }

    ticker_to_branch = {}
    for branch, companies in branches.items():
        for company in companies:
            ticker_to_branch[company] = branch

    print(ticker_to_branch)

    # Calculate the mean return for each category
    mean_return_per_category = high_conf_pos.groupby(high_conf_pos['Ticker'].map(ticker_to_branch))['midquote'].mean()
    # and sort this
    mean_return_per_category = mean_return_per_category.sort_values(ascending=False)

    # Plot this in a bar chart
    plt.figure(figsize=(20, 10))
    mean_return_per_category.plot(kind='bar', color='green')
    #plt.title(f'Mean Return for Each Category for the {selected_time} Second Model', fontsize=20)
    plt.xlabel('Category', fontsize=14)
    plt.ylabel('Mean Return', fontsize=14)
    plt.xticks(fontsize=8, rotation=45)
    plt.tight_layout()
    # save the picture to a file
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/mean_return_per_category_for_long_with_threshold_{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')
    #plt.show()



    # and plot this in a bar chart
    plt.figure(figsize=(20, 10))
    mean_return_per_ticker.plot(kind='bar', color='blue')
    #plt.title(f'Mean Return for Each Ticker for the {selected_time} Second Model', fontsize=20)
    plt.xlabel('Ticker', fontsize=14)
    plt.ylabel('Mean Return', fontsize=14)  
    plt.xticks(fontsize=8, rotation=90)
    plt.tight_layout()
    # save the picture to a file
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/mean_return_per_ticker_for_long_with_threshold_{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')
    #plt.show()

    import numpy as np
    import matplotlib.pyplot as plt

    # Assuming the calculate_negative_for_best function and val_df are defined elsewhere

    # Setup for grid search
    best_sharpe_ratio_negative = -np.inf
    best_y_negative = 0  # Updated for consistency with the naming convention

    # Define the range of y values
    w = 1.5 # in percent  
    percent_count = int(len(val_df) * (w/100))

    min_val = val_df['predicted_return'].nsmallest(percent_count).iloc[-1]
    y_values = np.linspace(min_val, 0.50, num=1000, endpoint=False)

    # Initialize an array to store Sharpe ratios for visualization
    sharpe_ratios = np.zeros(len(y_values))

    # Perform grid search over y values
    for i, y in enumerate(y_values):
        sharpe_ratio = calculate_negative_for_best(y, val_df)
        sharpe_ratios[i] = sharpe_ratio

        # Check for new best Sharpe ratio
        if sharpe_ratio > best_sharpe_ratio_negative:
            best_sharpe_ratio_negative = sharpe_ratio
            best_y_negative = y

    # Print the best Sharpe Ratio and corresponding y value
    print(f"Best Sharpe Ratio: {best_sharpe_ratio_negative:.4f}, Best Threshold: {best_y_negative:.4f}")

    # Plotting, adjusting to match the style of the first snippet
    plt.figure(figsize=(14, 7))  # Adjusted to match the original size

    # Plot all the Sharpe ratios as a line
    plt.plot(y_values, sharpe_ratios, linestyle='-', label='Sharpe Ratio')

    # Highlight the point with the best Sharpe ratio using a marker
    plt.plot(best_y_negative, best_sharpe_ratio_negative, 'o', color='red', label='Best Sharpe Ratio')

    #plt.title('Sharpe Ratio Optimization for Short Position')  # Updated title to be more descriptive
    plt.xlabel('Threshold')
    plt.ylabel('Sharpe Ratio')
    plt.grid(True)
    plt.legend()

    # save the picture to a file
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/validation_short_sharpe_ratio_optimal_{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')

    #plt.show()


    # save the best_sharpe_ratio_negative and best_y_negative to the excel_df
    excel_df.loc['Best Sharpe Ratio for validation for short', selected_time] = best_sharpe_ratio_negative
    excel_df.loc['Best threshold for validation for short', selected_time] = best_y_negative

    # make a print statement that calculates the sharpe ratio based on the optimal threshold for the long position in the test dataset
    print(f"Sharpe ratio based on the optimal threshold for the short position in the test dataset: {calculate_negative_for_best(best_y_negative, test_df):.8f}")

    # save the best sharpe ratio based on the test dataset to the excel_df
    excel_df.loc['Best Sharpe Ratio for test data for short', selected_time] = calculate_negative_for_best(best_y_negative, test_df)

    import pandas as pd

    # Creating a copy of the filtered DataFrame to avoid SettingWithCopyWarning
    high_conf_neg = test_df[test_df['predicted_return'] < best_y_negative].copy()

    # Now you can safely modify high_conf_neg without worrying about affecting test_df
    high_conf_neg['correct_prediction'] = ((high_conf_neg['predicted_return'] >= 0.5) & (high_conf_neg['midquote_target'] >= 0.5)) | ((high_conf_neg['predicted_return'] < 0.5) & (high_conf_neg['midquote_target'] < 0.5))

    # Calculate and print the overall accuracy
    overall_accuracy = high_conf_neg['correct_prediction'].mean()
    print(f"Overall Accuracy Score: {overall_accuracy:.4f}")

    # save the overall accuracy to the excel_df
    excel_df.loc['Overall accuracy for test data for short after optimal threshold', selected_time] = overall_accuracy

    # make a dictionary that contains the different x-axis values for the different time intervals
    x_dict = {'0,01': '%H:%M:%S', '0,1': '%H:%M:%S', '0,5': '%H:%M', '1': '%H:%M', '5': '%H:%M', '10': '%H:%M'}

    # Assuming high_conf_neg and selected_time are already defined

    # Group data by 'Time' and 'correct_prediction' to count occurrences
    prediction_counts = high_conf_neg.groupby(['Time', 'correct_prediction']).size().unstack(fill_value=0)

    prediction_counts.columns = prediction_counts.columns.map({True: 'Correct Prediction', False: 'Incorrect Prediction'})

    # Reset index to make 'Time' a column again (useful for seaborn plotting)
    prediction_counts.reset_index(inplace=True)
    # Convert the Time column to datetime
    prediction_counts['Time'] = pd.to_datetime(prediction_counts['Time'])

    #Create a date range from the first to the last timestamp with 1-second intervals
    date_range = pd.date_range(start=prediction_counts['Time'].min(), end=prediction_counts['Time'].max(), freq=time_dict[selected_time])

    prediction_counts.set_index('Time', inplace=True)
    prediction_counts_complete = prediction_counts.reindex(date_range, fill_value=0).reset_index()
    prediction_counts_complete.rename(columns={'index': 'Time'}, inplace=True)

    # make a momving average for the prediction_counts_complete for the incorrect prediction and the correct prediction columns
    prediction_counts_complete['correct_prediction_moving_average'] = prediction_counts_complete['Correct Prediction'].rolling(window=200).mean()
    prediction_counts_complete['incorrect_prediction_moving_average'] = prediction_counts_complete['Incorrect Prediction'].rolling(window=200).mean()

    prediction_counts_complete['sum_of_the_two'] = prediction_counts_complete['Correct Prediction'] + prediction_counts_complete['Incorrect Prediction']
    # remove the first 200 rows 
    prediction_counts_complete = prediction_counts_complete[200:]

    # Set the overall aesthetics
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(12, 9))

    # Plot the upper portion (4/5 of the upper half)
    ax1 = plt.subplot(2, 1, 1)
    sns.lineplot(data=prediction_counts_complete, x='Time', y='correct_prediction_moving_average', label='Correct Predictions (MA)', color='seagreen', ax=ax1)
    sns.lineplot(data=prediction_counts_complete, x='Time', y='incorrect_prediction_moving_average', label='Incorrect Predictions (MA)', color='salmon', ax=ax1)

    ax1.set_ylabel('Number of Trades (MA=200)', fontsize=16)
    ax1.tick_params(axis='both', which='major', labelsize=14)
    ax1.legend(loc='upper left', fontsize=14, title='Prediction Types')
    # delete the x axis label
    ax1.set_xlabel('')
    # delete the x axis ticks
    #ax1.set_xticks([])
    # make the vertical grid lines
    # for the x-axis only display the hour and minute
    ax1.xaxis.set_major_formatter(mdates.DateFormatter(str(x_dict[selected_time])))
    ax1.grid(True, linestyle='--', linewidth=0.5)  # lighter grid lines

    ax2 = plt.subplot(2, 1, 2)

    # Assuming prediction_counts_complete DataFrame is available
    sns.histplot(data=prediction_counts_complete, x='Time', weights='sum_of_the_two', bins=len(prediction_counts_complete), color='dimgray')
    ax2.set_xlabel('Time', fontsize=14)
    ax2.set_ylabel('Sum of Predictions', fontsize=16)
    ax2.tick_params(axis='both', which='major', labelsize=14)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter(str(x_dict[selected_time])))
    ax2.grid(True, linestyle='--', linewidth=0.5)  # lighter grid lines

    plt.tight_layout()

    # save the picture to a file
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/accuracy_over_time_short_{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')



    import matplotlib.pyplot as plt
    import numpy as np

    # Assuming `high_conf_neg`, `test_df`, `best_x_positive`, and `selected_time` are defined

    tickers_counts = high_conf_neg['Ticker'].value_counts().sort_values(ascending=False)

    # Calculate correct and incorrect counts based on 'correct_prediction' column
    correct_counts = high_conf_neg[high_conf_neg['correct_prediction'] == 1]['Ticker'].value_counts()
    incorrect_counts = high_conf_neg[high_conf_neg['correct_prediction'] == 0]['Ticker'].value_counts()

    # Assuming the second method is the one we're using for average spread
    average_spread_per_ticker = high_conf_neg.groupby('Ticker')['spread'].mean()
    average_spread_per_ticker = average_spread_per_ticker.round(2)

    # Making the figure and primary axis for the bar chart
    fig, ax1 = plt.subplots(figsize=(20, 10))

    # Plotting the correct and incorrect ticker counts as stacked bars
    ax1.bar(tickers_counts.index, correct_counts.reindex(tickers_counts.index, fill_value=0), color='green', label='Correct Predictions')
    ax1.bar(tickers_counts.index, incorrect_counts.reindex(tickers_counts.index, fill_value=0), bottom=correct_counts.reindex(tickers_counts.index, fill_value=0), color='red', label='Incorrect Predictions')
    ax1.set_xticks(range(len(tickers_counts)))
    ax1.set_xticklabels(tickers_counts.index, fontsize=8, rotation=90)
    ax1.set_ylabel('Number of Predictions', color='black', fontsize=18)
    ax1.tick_params(axis='y', labelcolor='black', labelsize=16)

    # Creating a secondary y-axis for the average spreads
    ax2 = ax1.twinx()

    # Prepare the data for the scatter plot
    x_values = np.arange(len(tickers_counts))
    y_values = np.array([average_spread_per_ticker.get(ticker, np.nan) for ticker in tickers_counts.index])

    # Plotting the average spreads as red dots on the secondary y-axis
    ax2.scatter(x_values, y_values, color='black', label='Average Spread (AS)')
    ax2.set_ylabel('Average Spread', color='black', fontsize=18)
    ax2.tick_params(axis='y', labelcolor='black', labelsize=16)

    # Calculate and plot the line of best fit for the red dots
    z = np.polyfit(x_values, y_values, 1)
    p = np.poly1d(z)
    ax2.plot(x_values, p(x_values), color='black', linestyle='--', label='Line of Best Fit for AS')  # Specifying color and line style separately


    # Adding legends
    ax1.legend(loc='upper left', fontsize=18)
    ax2.legend(loc='upper right', fontsize=18)

    ax2.grid(False)
    ax1.grid(False)

    ax1.set_xlim(left=-0.5, right=len(tickers_counts)-0.5)

    fig.tight_layout()

    # Setting the title with a specific fontsize
    #plt.title(f'Traded Stocks for short Strategy with Optimal Threshold of {best_x_positive:.4f} for the {selected_time} Second Model', fontsize=20)

    # save the picture to a file
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/traded_stocks_short_average_spread_and_ticker_count_{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')


    import matplotlib.pyplot as plt
    import numpy as np

    # Assuming calculate_combined_for_best function and val_df are defined elsewhere

    # Grid search setup
    best_sharpe_ratio = -np.inf
    best_x = 0
    best_y = 0

    w = 1.5 # in percent  
    percent_count = int(len(val_df) * (w/100))

    # Find the lowest predicted values in val_df
    min_val = val_df['predicted_return'].nsmallest(percent_count).iloc[-1]
    max_val = val_df['predicted_return'].nlargest(percent_count).iloc[-1]

    # Grid for x and y values
    x_values = np.linspace(0.50, max_val, num=50, endpoint=False) # adjust the num to a higher number for the real run
    y_values = np.linspace(min_val, 0.50, num=50, endpoint=False) # adjust the num to a higher number for the real run
    metric_grid = np.zeros((len(x_values), len(y_values)))

    # Perform grid search and populate the grid with Sharpe ratios
    for i, x in enumerate(x_values):
        for j, y in enumerate(y_values):
            if x <= y:  # Ensure x > y
                metric_grid[i, j] = np.nan
                continue
            
            combined_for_best = calculate_combined_for_best(x, y, val_df)

            # Update the metric grid
            metric_grid[i, j] = combined_for_best

            # Check for new best Sharpe ratio
            if combined_for_best > best_sharpe_ratio:
                best_sharpe_ratio = combined_for_best
                best_x = x
                best_y = y

    # Print the best Sharpe Ratio and corresponding x, y values
    print(f"Best Sharpe Ratio: {best_sharpe_ratio:.4f}, Best x: {best_x:.4f}, Best y: {best_y:.4f}")

    # Close any existing plots
    plt.close('all')

    # Plotting the heatmap of Sharpe ratios
    plt.figure(figsize=(10, 8))
    cax = plt.imshow(metric_grid, cmap='viridis', origin='lower', extent=[y_values.min(), y_values.max(), x_values.min(), x_values.max()], aspect='auto')
    cbar = plt.colorbar(cax, label='Sharpe Ratio')
    cbar.ax.set_ylabel('Sharpe Ratio', fontsize=16)  # Set font size for the colorbar label
    cbar.ax.tick_params(labelsize=12) 
    plt.xlabel('Lower Threshold for the Short Position', fontsize=16)
    plt.ylabel('Upper Threshold for the Long Position', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid(False)
    #plt.title(f'Heatmap of Sharpe Ratio Across Theresholds Combinations for {selected_time} Seconds')
    # save picture to a file
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/Validation_for_combined_sharpe_ratio_optimal_{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')



    # save the best_sharpe_ratio and best_x and best_y to the excel_df
    excel_df.loc['Best Sharpe Ratio for validation for combined', selected_time] = best_sharpe_ratio
    excel_df.loc['Best upper threshold for validation for combined', selected_time] = best_x
    excel_df.loc['Best lower threshold for validation for combined', selected_time] = best_y


    pd.options.display.float_format = '{:.7f}'.format

    high_conf_pos = test_df[test_df['predicted_return'] > best_x]
    high_conf_neg = test_df[test_df['predicted_return'] < best_y]

    # make a list to store both time and midquote values
    list_positive = high_conf_pos['midquote'].tolist()
    list_for_time_positive = high_conf_pos['Time'].tolist()

    # combine the two lists list_positive and list_for_time_positive to a dataframe
    Combineit_pos = pd.DataFrame(list_positive, list_for_time_positive)
    # sort after the time

    list_negative = high_conf_neg['midquote'].tolist()
    list_negative = [-x for x in list_negative] # for the short strategy (convert the value with negative value)
    list_for_time_negative = high_conf_neg['Time'].tolist()


    Combineit_neg = pd.DataFrame(list_negative, list_for_time_negative)

    # make the index a column
    Combineit_pos.reset_index(inplace=True)
    Combineit_neg.reset_index(inplace=True)

    # rename the columns
    if len(Combineit_pos)>0:
        Combineit_pos.columns = ['time', 'midquote']
        Combineit_pos = Combineit_pos.groupby('time').mean()
    else:
        Combineit_pos = pd.DataFrame(columns=['time', 'midquote'])


    if len(Combineit_neg)>0:
        Combineit_neg.columns = ['time', 'midquote']
        Combineit_neg = Combineit_neg.groupby('time').mean()
    else:
        Combineit_neg= pd.DataFrame(columns=['time', 'midquote'])


    if len(Combineit_neg)>0:
        if len(Combineit_pos>0):
            Combineit = Combineit_pos.merge(Combineit_neg, on='time', how='outer')
            Combineit.columns = ['midquote_positive', 'midquote_negative']

            count_positive = high_conf_pos['Time'].value_counts()
            count_negative = high_conf_neg['Time'].value_counts()

            Combineit = Combineit.merge(count_positive, left_on='time', right_on=count_positive.index, how='outer')
            Combineit = Combineit.merge(count_negative, left_on='time', right_on=count_negative.index, how='outer')

            Combineit.columns = ['time', 'return_positive', 'return_negative', 'count_positive', 'count_negative']
            # for nan values replace with 0
            Combineit['return_positive'] = Combineit['return_positive'].fillna(0)
            Combineit['return_negative'] = Combineit['return_negative'].fillna(0)
            Combineit['count_positive'] = Combineit['count_positive'].fillna(0)
            Combineit['count_negative'] = Combineit['count_negative'].fillna(0)

            Combineit['combined_return'] = (Combineit['return_positive'] * Combineit['count_positive'] / (Combineit['count_positive'] + Combineit['count_negative'])) + (Combineit['return_negative'] * Combineit['count_negative'] / (Combineit['count_positive'] + Combineit['count_negative']))


    combined_for_best = calculate_combined_for_best(best_x, best_y, test_df)

    # make print statement with text:
    print(f'The sharpe ratio for the best x and y values is: {combined_for_best}')

    # save the combined_for_best to the excel_df
    excel_df.loc['Best Sharpe Ratio for test data for combined', selected_time] = combined_for_best

    # Testing
    combined_df = pd.concat([high_conf_pos, high_conf_neg], axis=0)

    # Now you can safely modify combined_df without worrying about affecting test_df
    combined_df['correct_prediction'] = ((combined_df['predicted_return'] >= 0.5) & (combined_df['midquote_target'] >= 0.5)) | ((combined_df['predicted_return'] < 0.5) & (combined_df['midquote_target'] < 0.5))

    # Calculate and print the overall accuracy
    overall_accuracy = combined_df['correct_prediction'].mean()
    print(f"Overall Accuracy Score: {overall_accuracy:.4f}")


    # save the overall accuracy to the excel_df
    excel_df.loc['Overall accuracy for test data for combined after optimal threshold (long and short)', selected_time] = overall_accuracy


    # make a dictionary that contains the different x-axis values for the different time intervals
    x_dict = {'0,01': '%H:%M:%S', '0,1': '%H:%M:%S', '0,5': '%H:%M', '1': '%H:%M', '5': '%H:%M', '10': '%H:%M'}

    # Assuming combined_df and selected_time are already defined

    # Group data by 'Time' and 'correct_prediction' to count occurrences
    prediction_counts = combined_df.groupby(['Time', 'correct_prediction']).size().unstack(fill_value=0)

    prediction_counts.columns = prediction_counts.columns.map({True: 'Correct Prediction', False: 'Incorrect Prediction'})

    # Reset index to make 'Time' a column again (useful for seaborn plotting)
    prediction_counts.reset_index(inplace=True)
    # Convert the Time column to datetime
    prediction_counts['Time'] = pd.to_datetime(prediction_counts['Time'])

    #Create a date range from the first to the last timestamp with 1-second intervals
    date_range = pd.date_range(start=prediction_counts['Time'].min(), end=prediction_counts['Time'].max(), freq=time_dict[selected_time])

    prediction_counts.set_index('Time', inplace=True)
    prediction_counts_complete = prediction_counts.reindex(date_range, fill_value=0).reset_index()
    prediction_counts_complete.rename(columns={'index': 'Time'}, inplace=True)

    # make a momving average for the prediction_counts_complete for the incorrect prediction and the correct prediction columns
    prediction_counts_complete['correct_prediction_moving_average'] = prediction_counts_complete['Correct Prediction'].rolling(window=200).mean()
    prediction_counts_complete['incorrect_prediction_moving_average'] = prediction_counts_complete['Incorrect Prediction'].rolling(window=200).mean()

    prediction_counts_complete['sum_of_the_two'] = prediction_counts_complete['Correct Prediction'] + prediction_counts_complete['Incorrect Prediction']
    # remove the first 200 rows 
    prediction_counts_complete = prediction_counts_complete[200:]

    # Set the overall aesthetics
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(12, 9))

    # Plot the upper portion (4/5 of the upper half)
    ax1 = plt.subplot(2, 1, 1)
    sns.lineplot(data=prediction_counts_complete, x='Time', y='correct_prediction_moving_average', label='Correct Predictions (MA)', color='seagreen', ax=ax1)
    sns.lineplot(data=prediction_counts_complete, x='Time', y='incorrect_prediction_moving_average', label='Incorrect Predictions (MA)', color='salmon', ax=ax1)

    ax1.set_ylabel('Number of Trades (MA=200)', fontsize=16)
    ax1.tick_params(axis='both', which='major', labelsize=14)
    ax1.legend(loc='upper left', fontsize=14, title='Prediction Types')
    # delete the x axis label
    ax1.set_xlabel('')
    # delete the x axis ticks
    #ax1.set_xticks([])
    # make the vertical grid lines
    # for the x-axis only display the hour and minute
    ax1.xaxis.set_major_formatter(mdates.DateFormatter(str(x_dict[selected_time])))
    ax1.grid(True, linestyle='--', linewidth=0.5)  # lighter grid lines

    ax2 = plt.subplot(2, 1, 2)

    # Assuming prediction_counts_complete DataFrame is available
    sns.histplot(data=prediction_counts_complete, x='Time', weights='sum_of_the_two', bins=len(prediction_counts_complete), color='dimgray')
    ax2.set_xlabel('Time', fontsize=14)
    ax2.set_ylabel('Sum of Predictions', fontsize=16)
    ax2.tick_params(axis='both', which='major', labelsize=14)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter(str(x_dict[selected_time])))
    ax2.grid(True, linestyle='--', linewidth=0.5)  # lighter grid lines

    plt.tight_layout()

    # save the picture to a file
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/accuracy_over_time_combined_{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')



    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    # Assuming combined_df, best_x, best_y, selected_time, and time_dict are defined

    # Count the number of predictions above and below the thresholds
    above_threshold_counts = combined_df[combined_df['predicted_return'] >= best_x].groupby('Ticker').size()
    below_threshold_counts = combined_df[combined_df['predicted_return'] <= best_y].groupby('Ticker').size()

    # Calculate the average spread above and below the thresholds
    average_spread_above = combined_df[combined_df['predicted_return'] >= best_x].groupby('Ticker')['spread'].mean()
    average_spread_below = combined_df[combined_df['predicted_return'] <= best_y].groupby('Ticker')['spread'].mean()

    # Total counts and sorted tickers
    tickers = combined_df['Ticker'].unique()
    total_counts = above_threshold_counts.add(below_threshold_counts, fill_value=0)
    sorted_tickers = total_counts.sort_values(ascending=False).index

    # Reindexing to ensure all data aligns properly
    above_threshold_counts = above_threshold_counts.reindex(sorted_tickers, fill_value=0)
    below_threshold_counts = below_threshold_counts.reindex(sorted_tickers, fill_value=0)
    average_spread_above = average_spread_above.reindex(sorted_tickers, fill_value=np.nan)
    average_spread_below = average_spread_below.reindex(sorted_tickers, fill_value=np.nan)

    # Creating the figure and primary axis for the bar chart
    fig, ax1 = plt.subplots(figsize=(20, 10))
    ind = np.arange(len(sorted_tickers))

    # Plotting the bar charts for above and below threshold predictions
    ax1.bar(ind, below_threshold_counts, color='red', label='Short Strategy (Predictions below {:.4f})'.format(best_y))
    ax1.bar(ind, above_threshold_counts, bottom=below_threshold_counts, color='green', label='Long Strategy (Predictions above {:.4f})'.format(best_x))

    # Creating a secondary y-axis for the average spreads
    ax2 = ax1.twinx()

    # Scatter plots for the average spreads
    ax2.scatter(ind, average_spread_below, color='darkred', alpha=0.5, label='Average Spread Below Threshold')
    ax2.scatter(ind, average_spread_above, color='darkgreen', alpha=0.5, label='Average Spread Above Threshold')

    # Calculating and plotting lines of best fit for average spreads
    z_below = np.polyfit(ind[~np.isnan(average_spread_below)], average_spread_below.dropna(), 1)
    p_below = np.poly1d(z_below)
    ax2.plot(ind, p_below(ind), 'r--', alpha=0.75)

    z_above = np.polyfit(ind[~np.isnan(average_spread_above)], average_spread_above.dropna(), 1)
    p_above = np.poly1d(z_above)
    ax2.plot(ind, p_above(ind), 'g--', alpha=0.75)

    # Setting labels, ticks, legends, and formatting
    ax1.set_xticks(ind)
    ax1.set_xticklabels(sorted_tickers, rotation=90, fontsize=8)
    ax1.set_ylabel('Number of Predictions', fontsize=18)
    ax2.set_ylabel('Average Spread', fontsize=18)

    # Adjusting tick label size
    #ax1.tick_params(axis='x', labelsize=8)  # Set fontsize for x-axis ticks
    ax1.tick_params(axis='y', labelsize=14)  # Set fontsize for y-axis ticks
    ax2.tick_params(axis='y', labelsize=14)  # Set fontsize for secondary y-axis ticks

    ax1.legend(loc='upper left', fontsize=18)
    ax2.legend(loc='upper right', fontsize=18)

    ax1.grid(False)
    ax2.grid(False)
    ax1.set_xlim(left=-0.5, right=len(sorted_tickers)-0.5)

    fig.tight_layout()

    # Save the picture to a file
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/number_of_trades_and_average_spread_per_ticker_{time_dict[selected_time]}.png', dpi=300, bbox_inches='tight')



    pd.options.display.float_format = '{:.7f}'.format

    x = best_x
    y = best_y


    high_conf_pos = test_df[test_df['predicted_return'] > x]
    high_conf_neg = test_df[test_df['predicted_return'] < y]

    # make a list to store both time and midquote values
    list_positive = high_conf_pos['midquote'].tolist()
    list_for_time_positive = high_conf_pos['Time'].tolist()

    # combine the two lists list_positive and list_for_time_positive to a dataframe
    Combineit_pos = pd.DataFrame(list_positive, list_for_time_positive)
    # sort after the time

    list_negative = high_conf_neg['midquote'].tolist()
    list_negative = [-x for x in list_negative] # for the short strategy (convert the value with negative value)
    list_for_time_negative = high_conf_neg['Time'].tolist()


    Combineit_neg = pd.DataFrame(list_negative, list_for_time_negative)

    # make the index a column
    Combineit_pos.reset_index(inplace=True)
    Combineit_neg.reset_index(inplace=True)

    # rename the columns
    if len(Combineit_pos)>0:
        Combineit_pos.columns = ['time', 'midquote']
        Combineit_pos = Combineit_pos.groupby('time').mean()
    else:
        Combineit_pos = pd.DataFrame(columns=['time', 'midquote'])


    if len(Combineit_neg)>0:
        Combineit_neg.columns = ['time', 'midquote']
        Combineit_neg = Combineit_neg.groupby('time').mean()
    else:
        Combineit_neg= pd.DataFrame(columns=['time', 'midquote'])


    if len(Combineit_neg)>0:
        if len(Combineit_pos>0):
            Combineit = Combineit_pos.merge(Combineit_neg, on='time', how='outer')
            Combineit.columns = ['midquote_positive', 'midquote_negative']

            count_positive = high_conf_pos['Time'].value_counts()
            count_negative = high_conf_neg['Time'].value_counts()

            Combineit = Combineit.merge(count_positive, left_on='time', right_on=count_positive.index, how='outer')
            Combineit = Combineit.merge(count_negative, left_on='time', right_on=count_negative.index, how='outer')

            Combineit.columns = ['time', 'return_positive', 'return_negative', 'count_positive', 'count_negative']
            # for nan values replace with 0
            Combineit['return_positive'] = Combineit['return_positive'].fillna(0)
            Combineit['return_negative'] = Combineit['return_negative'].fillna(0)
            Combineit['count_positive'] = Combineit['count_positive'].fillna(0)
            Combineit['count_negative'] = Combineit['count_negative'].fillna(0)

            Combineit['combined_return'] = (Combineit['return_positive'] * Combineit['count_positive'] / (Combineit['count_positive'] + Combineit['count_negative'])) + (Combineit['return_negative'] * Combineit['count_negative'] / (Combineit['count_positive'] + Combineit['count_negative']))



    if len(Combineit_neg)==0:
        Combineit = Combineit_pos
        Combineit.columns = ['midquote_positive']
        count_positive = high_conf_pos['Time'].value_counts()
        Combineit = Combineit.merge(count_positive, left_on='time', right_on=count_positive.index, how='outer')
        Combineit.columns = ['time', 'return_positive', 'count_positive']
        Combineit['return_positive'] = Combineit['return_positive'].fillna(0)
        Combineit['count_positive'] = Combineit['count_positive'].fillna(0)
        Combineit['combined_return'] = Combineit['return_positive']

    if len(Combineit_pos)==0:
        Combineit = Combineit_neg
        Combineit.columns = ['midquote_negative']
        count_negative = high_conf_neg['Time'].value_counts()
        Combineit = Combineit.merge(count_negative, left_on='time', right_on=count_negative.index, how='outer')
        Combineit.columns = ['time', 'return_negative', 'count_negative']
        Combineit['return_negative'] = Combineit['return_negative'].fillna(0)
        Combineit['count_negative'] = Combineit['count_negative'].fillna(0)
        Combineit['combined_return'] = Combineit['return_negative']


    combined_for_best = Combineit['combined_return'].mean()/Combineit['combined_return'].std()

    # make print statement with text:
    print(f'The combined sharpe ratio for the best x and y values is: {combined_for_best}')


    # save the combined_for_best to the excel_df
    excel_df.loc['Best Sharpe Ratio for test data for combined', selected_time] = combined_for_best

    # calculate the sharpes ratios for the positive and negative returns
    sharpe_positive = Combineit_pos['midquote'].mean()/Combineit_pos['midquote'].std()
    sharpe_negative = Combineit_neg['midquote'].mean()/Combineit_neg['midquote'].std()

    # make print statements for the sharpe ratios with text
    print('The sharpe ratio for the positive returns is:', sharpe_positive)
    print('The sharpe ratio for the negative returns is:', sharpe_negative)

    # Save the sharpe ratios to the excel_df
    excel_df.loc['Sharpe Ratio for long returns for test data based on the optimal combined threshold', selected_time] = sharpe_positive
    excel_df.loc['Sharpe Ratio for short returns for test data based on the optimal combined threshold', selected_time] = sharpe_negative

    Combineit_1 = Combineit.iloc[::4, :]
    Combineit_2 = Combineit.iloc[1::4, :]
    Combineit_3 = Combineit.iloc[2::4, :]
    Combineit_4 = Combineit.iloc[3::4, :]

    invested_money = 100

    def calculate_final_investment_value(df):
        initial_investment = invested_money/4
        current_investment = initial_investment
        investment_values = []

        for index, row in df.iterrows():
            current_investment *= (1 + row['combined_return'])
            investment_values.append(current_investment)

        return current_investment, investment_values

    # Assuming Combineit_1, Combineit_2, Combineit_3, and Combineit_4 are your DataFrames
    dataframes = [Combineit_1, Combineit_2, Combineit_3, Combineit_4]

    # Iterate over each DataFrame and calculate the final investment value
    for i, df in enumerate(dataframes, start=1):
        final_value, _ = calculate_final_investment_value(df)
        print(f"Final investment value for Combineit_{i}: {final_value:.8f}")

    # and sum the final investment values
    final_investment_value = sum([calculate_final_investment_value(df)[0] for df in dataframes])
    print(f"Sum of final investment values: {final_investment_value:.8f}")

    print(f'Money earned by investing {invested_money} on strategy: {final_investment_value - invested_money:.8f}')
    print(f'Return on combined investment: {((final_investment_value - invested_money) / invested_money)*100:.8f}%')


    # save the results to the excel_df
    excel_df.loc['Sum of final investment values for the combined strategy(with two thresholds)', selected_time] = final_investment_value
    excel_df.loc['Money earned by investing 100 on combined strategy (with two thresholds)', selected_time] = final_investment_value - invested_money
    excel_df.loc['Return on combined investment (with two thresholds)', selected_time] = ((final_investment_value - invested_money) / invested_money)*100

    def calculate_final_investment_value(df):
        initial_investment = invested_money/4
        current_investment = initial_investment
        investment_values = []
        for index, row in df.iterrows():
            current_investment *= (1 + row['midquote'])
            investment_values.append(current_investment)
        return current_investment, investment_values

    def calculate_positive_return_for_best(x, df):
        pd.options.display.float_format = '{:.7f}'.format

        high_conf_pos = df[df['predicted_return'] > x]

        # make a list to store both time and midquote values
        list_positive = high_conf_pos['midquote'].tolist()
        list_for_time_positive = high_conf_pos['Time'].tolist()

        # combine the two lists list_positive and list_for_time_positive to a dataframe
        Combineit_pos = pd.DataFrame(list_positive)
        # sort after the time

        # make the index a column
        Combineit_pos.reset_index(inplace=True)

        # rename the columns
        if len(Combineit_pos)>0:
            Combineit_pos.columns = ['time', 'midquote']
            Combineit_pos = Combineit_pos.groupby('time').mean()
        else:
            Combineit_pos = pd.DataFrame(columns=['time', 'midquote'])

        #Combineit_pos.columns = ['midquote_positive']

        Combineit_pos_1 = Combineit_pos.iloc[::4, :]
        Combineit_pos_2 = Combineit_pos.iloc[1::4, :]
        Combineit_pos_3 = Combineit_pos.iloc[2::4, :]
        Combineit_pos_4 = Combineit_pos.iloc[3::4, :]

        invested_money = 100

        # Assuming Combineit_pos_1, Combineit_pos_2, Combineit_pos_3, and Combineit_pos_4 are your DataFrames
        dataframes = [Combineit_pos_1, Combineit_pos_2, Combineit_pos_3, Combineit_pos_4]

        # Iterate over each DataFrame and calculate the final investment value
        for i, df in enumerate(dataframes, start=1):
            final_value, _ = calculate_final_investment_value(df)
            #print(f"Final investment value for Combineit_pos_{i}: {final_value:.8f}")

        # and sum the final investment values
        final_investment_value = sum([calculate_final_investment_value(df)[0] for df in dataframes])

        return(((final_investment_value - invested_money) / invested_money)*100)


    calculate_positive_return_for_best(best_x_positive, test_df)

    # save the results to the excel_df
    excel_df.loc['Return on long investment only (based on optimal long threshold only)', selected_time] = calculate_positive_return_for_best(best_x_positive, test_df)

    def calculate_final_investment_value(df):
        initial_investment = invested_money/4
        current_investment = initial_investment
        investment_values = []
        for index, row in df.iterrows():
            current_investment *= (1 + row['midquote'])
            investment_values.append(current_investment)
        return current_investment, investment_values

    def calculate_negative_return_for_best(x, df):
        pd.options.display.float_format = '{:.7f}'.format


        high_conf_neg = df[df['predicted_return'] < y]

        # sort after the time

        list_negative = high_conf_neg['midquote'].tolist()
        list_negative = [-x for x in list_negative] # for the short strategy (convert the value with negative value)
        list_for_time_negative = high_conf_neg['Time'].tolist()


        Combineit_neg = pd.DataFrame(list_negative, list_for_time_negative)

        # make the index a column
        Combineit_neg.reset_index(inplace=True)


        if len(Combineit_neg)>0:
            Combineit_neg.columns = ['time', 'midquote']
            Combineit_neg = Combineit_neg.groupby('time').mean()
        else:
            Combineit_neg= pd.DataFrame(columns=['time', 'midquote'])

            #Combineit_neg.columns = ['midquote_negative']

        Combineit_neg_1 = Combineit_neg.iloc[::4, :]
        Combineit_neg_2 = Combineit_neg.iloc[1::4, :]
        Combineit_neg_3 = Combineit_neg.iloc[2::4, :]
        Combineit_neg_4 = Combineit_neg.iloc[3::4, :]

        invested_money = 100

        # Assuming Combineit_neg_1, Combineit_neg_2, Combineit_neg_3, and Combineit_neg_4 are your DataFrames
        dataframes = [Combineit_neg_1, Combineit_neg_2, Combineit_neg_3, Combineit_neg_4]

        # Iterate over each DataFrame and calculate the final investment value
        for i, df in enumerate(dataframes, start=1):
            final_value, _ = calculate_final_investment_value(df)
            #print(f"Final investment value for Combineit_neg_{i}: {final_value:.8f}")

        # and sum the final investment values
        final_investment_value = sum([calculate_final_investment_value(df)[0] for df in dataframes])

        return(((final_investment_value - invested_money) / invested_money)*100)


    calculate_negative_return_for_best(best_y_negative, test_df)

    # save the results to the excel_df
    excel_df.loc['Return on short investment only (based on optimal short threshold only)', selected_time] = calculate_negative_return_for_best(best_y_negative, test_df)


    Combineit_pos_1 = Combineit_pos.iloc[::4, :]
    Combineit_pos_2 = Combineit_pos.iloc[1::4, :]
    Combineit_pos_3 = Combineit_pos.iloc[2::4, :]
    Combineit_pos_4 = Combineit_pos.iloc[3::4, :]

    invested_money = 100

    def calculate_final_investment_value(df):
        initial_investment = invested_money/4
        current_investment = initial_investment
        investment_values = []

        for index, row in df.iterrows():
            current_investment *= (1 + row['midquote'])
            investment_values.append(current_investment)

        return current_investment, investment_values

    # Assuming Combineit_pos_1, Combineit_pos_2, Combineit_pos_3, and Combineit_pos_4 are your DataFrames
    dataframes = [Combineit_pos_1, Combineit_pos_2, Combineit_pos_3, Combineit_pos_4]

    # Iterate over each DataFrame and calculate the final investment value
    for i, df in enumerate(dataframes, start=1):
        final_value, _ = calculate_final_investment_value(df)
        #print(f"Final investment value for Combineit_pos_{i}: {final_value:.8f}")

    # and sum the final investment values
    final_investment_value = sum([calculate_final_investment_value(df)[0] for df in dataframes])
    print(f"Sum of final investment values: {final_investment_value:.8f}")

    print(f'Money earned by investing {invested_money} on strategy: {final_investment_value - invested_money:.8f}')
    print(f'Return on positive investment: {((final_investment_value - invested_money) / invested_money)*100:.8f}%')


    # save the results to the excel_df
    excel_df.loc['Sum of final investment values for the long strategy only (but with the upper thresholds from the combined strategy)', selected_time] = final_investment_value


    Combineit_neg_1 = Combineit_neg.iloc[::4, :]
    Combineit_neg_2 = Combineit_neg.iloc[1::4, :]
    Combineit_neg_3 = Combineit_neg.iloc[2::4, :]
    Combineit_neg_4 = Combineit_neg.iloc[3::4, :]

    invested_money = 100

    def calculate_final_investment_value(df):
        initial_investment = invested_money/4
        current_investment = initial_investment
        investment_values = []

        for index, row in df.iterrows():
            current_investment *= (1 + row['midquote'])
            investment_values.append(current_investment)

        return current_investment, investment_values

    # Assuming Combineit_neg_1, Combineit_neg_2, Combineit_neg_3, and Combineit_neg_4 are your DataFrames
    dataframes = [Combineit_neg_1, Combineit_neg_2, Combineit_neg_3, Combineit_neg_4]

    # Iterate over each DataFrame and calculate the final investment value
    for i, df in enumerate(dataframes, start=1):
        final_value, _ = calculate_final_investment_value(df)
        #print(f"Final investment value for Combineit_neg_{i}: {final_value:.8f}")

    # and sum the final investment values
    final_investment_value = sum([calculate_final_investment_value(df)[0] for df in dataframes])
    print(f"Sum of final investment values: {final_investment_value:.8f}")

    print(f'Money earned by investing {invested_money} on strategy: {final_investment_value - invested_money:.8f}')
    print(f'Return on negative investment: {((final_investment_value - invested_money) / invested_money)*100:.8f}%')


    # save the results to the excel_df
    excel_df.loc['Sum of final investment values for the short strategy only (but with the lower thresholds from the combined strategy)', selected_time] = final_investment_value


    def calculate_combined_for_best(x, y, df):
        pd.options.display.float_format = '{:.7f}'.format

        high_conf_pos = val_df[val_df['predicted_return'] > x]
        high_conf_neg = val_df[val_df['predicted_return'] < y]

        # make a list to store both time and midquote values
        list_positive = high_conf_pos['midquote'].tolist()
        list_for_time_positive = high_conf_pos['Time'].tolist()

        # combine the two lists list_positive and list_for_time_positive to a dataframe
        Combineit_pos = pd.DataFrame(list_positive, list_for_time_positive)
        # sort after the time

        list_negative = high_conf_neg['midquote'].tolist()
        list_negative = [-x for x in list_negative] # for the short strategy (convert the value with negative value)
        list_for_time_negative = high_conf_neg['Time'].tolist()


        Combineit_neg = pd.DataFrame(list_negative, list_for_time_negative)

        # make the index a column
        Combineit_pos.reset_index(inplace=True)
        Combineit_neg.reset_index(inplace=True)

        # rename the columns
        if len(Combineit_pos)>0:
            Combineit_pos.columns = ['time', 'midquote']
            Combineit_pos = Combineit_pos.groupby('time').mean()
        else:
            Combineit_pos = pd.DataFrame(columns=['time', 'midquote'])


        if len(Combineit_neg)>0:
            Combineit_neg.columns = ['time', 'midquote']
            Combineit_neg = Combineit_neg.groupby('time').mean()
        else:
            Combineit_neg= pd.DataFrame(columns=['time', 'midquote'])


        if len(Combineit_neg)>0:
            if len(Combineit_pos>0):
                Combineit = Combineit_pos.merge(Combineit_neg, on='time', how='outer')
                Combineit.columns = ['midquote_positive', 'midquote_negative']

                count_positive = high_conf_pos['Time'].value_counts()
                count_negative = high_conf_neg['Time'].value_counts()

                Combineit = Combineit.merge(count_positive, left_on='time', right_on=count_positive.index, how='outer')
                Combineit = Combineit.merge(count_negative, left_on='time', right_on=count_negative.index, how='outer')

                Combineit.columns = ['time', 'return_positive', 'return_negative', 'count_positive', 'count_negative']
                # for nan values replace with 0
                Combineit['return_positive'] = Combineit['return_positive'].fillna(0)
                Combineit['return_negative'] = Combineit['return_negative'].fillna(0)
                Combineit['count_positive'] = Combineit['count_positive'].fillna(0)
                Combineit['count_negative'] = Combineit['count_negative'].fillna(0)

                Combineit['combined_return'] = (Combineit['return_positive'] * Combineit['count_positive'] / (Combineit['count_positive'] + Combineit['count_negative'])) + (Combineit['return_negative'] * Combineit['count_negative'] / (Combineit['count_positive'] + Combineit['count_negative']))



        if len(Combineit_neg)==0:
            Combineit = Combineit_pos
            Combineit.columns = ['midquote_positive']
            count_positive = high_conf_pos['Time'].value_counts()
            Combineit = Combineit.merge(count_positive, left_on='time', right_on=count_positive.index, how='outer')
            Combineit.columns = ['time', 'return_positive', 'count_positive']
            Combineit['return_positive'] = Combineit['return_positive'].fillna(0)
            Combineit['count_positive'] = Combineit['count_positive'].fillna(0)
            Combineit['combined_return'] = Combineit['return_positive']

        if len(Combineit_pos)==0:
            Combineit = Combineit_neg
            Combineit.columns = ['midquote_negative']
            count_negative = high_conf_neg['Time'].value_counts()
            Combineit = Combineit.merge(count_negative, left_on='time', right_on=count_negative.index, how='outer')
            Combineit.columns = ['time', 'return_negative', 'count_negative']
            Combineit['return_negative'] = Combineit['return_negative'].fillna(0)
            Combineit['count_negative'] = Combineit['count_negative'].fillna(0)
            Combineit['combined_return'] = Combineit['return_negative']

        Combineit_1 = Combineit.iloc[::4, :]
        Combineit_2 = Combineit.iloc[1::4, :]
        Combineit_3 = Combineit.iloc[2::4, :]
        Combineit_4 = Combineit.iloc[3::4, :]

        invested_money = 1000000

        def calculate_final_investment_value(df):
            initial_investment = invested_money/4
            current_investment = initial_investment
            investment_values = []

            for index, row in df.iterrows():
                current_investment *= (1 + row['combined_return'])
                investment_values.append(current_investment)

            return current_investment, investment_values

        # Assuming Combineit_1, Combineit_2, Combineit_3, and Combineit_4 are your DataFrames
        dataframes = [Combineit_1, Combineit_2, Combineit_3, Combineit_4]

        # Iterate over each DataFrame and calculate the final investment value
        for i, df in enumerate(dataframes, start=1):
            final_value, _ = calculate_final_investment_value(df)

        # and sum the final investment values
        final_investment_value = sum([calculate_final_investment_value(df)[0] for df in dataframes])

        return_metric = ((final_investment_value - invested_money) / invested_money)*100

        return(return_metric)


    import numpy as np
    import matplotlib.pyplot as plt

    # Assuming calculate_combined_for_best, val_df, and selected_time are already defined

    # Grid search setup
    best_return = -np.inf
    best_x = 0
    best_y = 0

    w = 1.5  # in percent
    percent_count = int(len(val_df) * (w / 100))

    # Find the lowest and highest predicted values in val_df
    min_val = val_df['predicted_return'].nsmallest(percent_count).iloc[-1]
    max_val = val_df['predicted_return'].nlargest(percent_count).iloc[-1]

    # Grid for x and y values
    x_values = np.linspace(0.50, max_val, num=40, endpoint=False)  # Adjusted as per the new setup
    y_values = np.linspace(min_val, 0.50, num=40, endpoint=False)  # Adjusted as per the new setup

    metric_grid = np.zeros((len(x_values), len(y_values)))

    # Perform grid search and populate the grid with Sharpe ratios
    for i, x in enumerate(x_values):
        for j, y in enumerate(y_values):
            if x <= y:  # Ensure x > y for valid combinations
                metric_grid[i, j] = np.nan
                continue
            
            combined_for_best = calculate_combined_for_best(x, y, val_df)

            # Update the metric grid
            metric_grid[i, j] = combined_for_best

            # Check for new best Sharpe ratio
            if combined_for_best > best_return:
                best_return = combined_for_best
                best_x = x
                best_y = y

    # Print the best Sharpe Ratio and corresponding x, y values
    print(f"Best return: {best_return:.4f}, Best x: {best_x:.4f}, Best y: {best_y:.4f}")

    # Plotting the heatmap of Sharpe ratios
    plt.figure(figsize=(10, 8))
    plt.imshow(metric_grid, cmap='viridis', origin='lower',
               extent=[y_values.min(), y_values.max(), x_values.min(), x_values.max()], aspect='auto')
    plt.colorbar(label='Return')
    plt.xlabel('Threshold wrt. the Prediction for Short Position')
    plt.ylabel('Threshold wrt. the Prediction for Long Position')
    #plt.title(f'Heatmap of Returns Across Thresholds Combinations for {selected_time} Seconds')
    # save the picture to a file
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/heatmap_returns_based_on_optimization_for_return_combined{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')
    #plt.show()


    # save the best_return, best_x, best_y to the excel_df
    excel_df.loc['Best Return for validation for combined based on the optimization for Return', selected_time] = best_return
    excel_df.loc['Optimal upper threshold for validation for combined based on optimization for return', selected_time] = best_x
    excel_df.loc['Optimal lower threshold for validation for combined based on optimization for return', selected_time] = best_y

    calculate_combined_for_best(best_x, best_y, test_df)


    # save the results to the excel_df
    excel_df.loc['Best Return for test data for combined based on the optimization for Return', selected_time] = best_return


    pd.options.display.float_format = '{:.7f}'.format

    high_conf_pos = test_df[test_df['predicted_return'] > best_x]
    high_conf_neg = test_df[test_df['predicted_return'] < best_y]

    # make a list to store both time and midquote values
    list_positive = high_conf_pos['midquote'].tolist()
    list_for_time_positive = high_conf_pos['Time'].tolist()

    # combine the two lists list_positive and list_for_time_positive to a dataframe
    Combineit_pos = pd.DataFrame(list_positive, list_for_time_positive)
    # sort after the time

    list_negative = high_conf_neg['midquote'].tolist()
    list_negative = [-x for x in list_negative] # for the short strategy (convert the value with negative value)
    list_for_time_negative = high_conf_neg['Time'].tolist()


    Combineit_neg = pd.DataFrame(list_negative, list_for_time_negative)

    # make the index a column
    Combineit_pos.reset_index(inplace=True)
    Combineit_neg.reset_index(inplace=True)

    # rename the columns
    if len(Combineit_pos)>0:
        Combineit_pos.columns = ['time', 'midquote']
        Combineit_pos = Combineit_pos.groupby('time').mean()
    else:
        Combineit_pos = pd.DataFrame(columns=['time', 'midquote'])


    if len(Combineit_neg)>0:
        Combineit_neg.columns = ['time', 'midquote']
        Combineit_neg = Combineit_neg.groupby('time').mean()
    else:
        Combineit_neg= pd.DataFrame(columns=['time', 'midquote'])


    if len(Combineit_neg)>0:
        if len(Combineit_pos>0):
            Combineit = Combineit_pos.merge(Combineit_neg, on='time', how='outer')
            Combineit.columns = ['midquote_positive', 'midquote_negative']

            count_positive = high_conf_pos['Time'].value_counts()
            count_negative = high_conf_neg['Time'].value_counts()

            Combineit = Combineit.merge(count_positive, left_on='time', right_on=count_positive.index, how='outer')
            Combineit = Combineit.merge(count_negative, left_on='time', right_on=count_negative.index, how='outer')

            Combineit.columns = ['time', 'return_positive', 'return_negative', 'count_positive', 'count_negative']
            # for nan values replace with 0
            Combineit['return_positive'] = Combineit['return_positive'].fillna(0)
            Combineit['return_negative'] = Combineit['return_negative'].fillna(0)
            Combineit['count_positive'] = Combineit['count_positive'].fillna(0)
            Combineit['count_negative'] = Combineit['count_negative'].fillna(0)

            Combineit['combined_return'] = (Combineit['return_positive'] * Combineit['count_positive'] / (Combineit['count_positive'] + Combineit['count_negative'])) + (Combineit['return_negative'] * Combineit['count_negative'] / (Combineit['count_positive'] + Combineit['count_negative']))



    if len(Combineit_neg)==0:
        Combineit = Combineit_pos
        Combineit.columns = ['midquote_positive']
        count_positive = high_conf_pos['Time'].value_counts()
        Combineit = Combineit.merge(count_positive, left_on='time', right_on=count_positive.index, how='outer')
        Combineit.columns = ['time', 'return_positive', 'count_positive']
        Combineit['return_positive'] = Combineit['return_positive'].fillna(0)
        Combineit['count_positive'] = Combineit['count_positive'].fillna(0)
        Combineit['combined_return'] = Combineit['return_positive']

    if len(Combineit_pos)==0:
        Combineit = Combineit_neg
        Combineit.columns = ['midquote_negative']
        count_negative = high_conf_neg['Time'].value_counts()
        Combineit = Combineit.merge(count_negative, left_on='time', right_on=count_negative.index, how='outer')
        Combineit.columns = ['time', 'return_negative', 'count_negative']
        Combineit['return_negative'] = Combineit['return_negative'].fillna(0)
        Combineit['count_negative'] = Combineit['count_negative'].fillna(0)
        Combineit['combined_return'] = Combineit['return_negative']


    combined_for_best = Combineit['combined_return'].mean()/Combineit['combined_return'].std()

    # print the sharpe ratio with the oprimal x and y values for the return optimization
    print(f'This is the sharpe ratio for the optimal x and y values: {combined_for_best}')

    #save the sharpe ratio to the excel_df
    excel_df.loc['Sharpe Ratio for test data for combined based on the optimization for Return', selected_time] = combined_for_best


    # calculate the sharpes ratios for the positive and negative returns
    sharpe_positive = Combineit_pos['midquote'].mean()/Combineit_pos['midquote'].std()
    sharpe_negative = Combineit_neg['midquote'].mean()/Combineit_neg['midquote'].std()

    # make print statements for the sharpe ratios with text
    print('The sharpe ratio for the positive returns is:', sharpe_positive)
    print('The sharpe ratio for the negative returns is:', sharpe_negative)

    # Save the sharpe ratios to the excel_df
    excel_df.loc['Sharpe Ratio for long returns for test data based on the optimal combined threshold for the optimization for Return', selected_time] = sharpe_positive
    excel_df.loc['Sharpe Ratio for short returns for test data based on the optimal combined threshold for the optimization for Return', selected_time] = sharpe_negative


    Combineit_1 = Combineit.iloc[::4, :]
    Combineit_2 = Combineit.iloc[1::4, :]
    Combineit_3 = Combineit.iloc[2::4, :]
    Combineit_4 = Combineit.iloc[3::4, :]

    invested_money = 100

    def calculate_final_investment_value(df):
        initial_investment = invested_money/4
        current_investment = initial_investment
        investment_values = []

        for index, row in df.iterrows():
            current_investment *= (1 + row['combined_return'])
            investment_values.append(current_investment)

        return current_investment, investment_values

    # Assuming Combineit_1, Combineit_2, Combineit_3, and Combineit_4 are your DataFrames
    dataframes = [Combineit_1, Combineit_2, Combineit_3, Combineit_4]

    # Iterate over each DataFrame and calculate the final investment value
    for i, df in enumerate(dataframes, start=1):
        final_value, _ = calculate_final_investment_value(df)
        print(f"Final investment value for Combineit_{i}: {final_value:.8f}")

    # and sum the final investment values
    final_investment_value = sum([calculate_final_investment_value(df)[0] for df in dataframes])
    print(f"Sum of final investment values: {final_investment_value:.8f}")

    print(f'Money earned by investing {invested_money} on strategy: {final_investment_value - invested_money:.8f}')
    print(f'Return on combined investment: {((final_investment_value - invested_money) / invested_money)*100:.8f}%')


    # save the results to the excel_df
    excel_df.loc['Sum of final investment values for the combined strategy(with two thresholds) for the optimization for Return', selected_time] = final_investment_value
    excel_df.loc['Money earned by investing 100 on combined strategy (with two thresholds) for the optimization for Return', selected_time] = final_investment_value - invested_money
    excel_df.loc['Return on combined investment (with two thresholds) for the optimization for Return', selected_time] = ((final_investment_value - invested_money) / invested_money)*100


    Combineit_pos_1 = Combineit_pos.iloc[::4, :]
    Combineit_pos_2 = Combineit_pos.iloc[1::4, :]
    Combineit_pos_3 = Combineit_pos.iloc[2::4, :]
    Combineit_pos_4 = Combineit_pos.iloc[3::4, :]

    invested_money = 100

    def calculate_final_investment_value(df):
        initial_investment = invested_money/4
        current_investment = initial_investment
        investment_values = []

        for index, row in df.iterrows():
            current_investment *= (1 + row['midquote'])
            investment_values.append(current_investment)

        return current_investment, investment_values

    # Assuming Combineit_pos_1, Combineit_pos_2, Combineit_pos_3, and Combineit_pos_4 are your DataFrames
    dataframes = [Combineit_pos_1, Combineit_pos_2, Combineit_pos_3, Combineit_pos_4]

    # Iterate over each DataFrame and calculate the final investment value
    for i, df in enumerate(dataframes, start=1):
        final_value, _ = calculate_final_investment_value(df)
        #print(f"Final investment value for Combineit_pos_{i}: {final_value:.8f}")

    # and sum the final investment values
    final_investment_value = sum([calculate_final_investment_value(df)[0] for df in dataframes])
    print(f"Sum of final investment values: {final_investment_value:.8f}")

    print(f'Money earned by investing {invested_money} on strategy: {final_investment_value - invested_money:.8f}')
    print(f'Return on positive investment: {((final_investment_value - invested_money) / invested_money)*100:.8f}%')


    # save the return on positive investment to the excel_df
    excel_df.loc['Return on long investment only (based on optimal long threshold only) for the optimization for Return', selected_time] = ((final_investment_value - invested_money) / invested_money)*100

    Combineit_neg_1 = Combineit_neg.iloc[::4, :]
    Combineit_neg_2 = Combineit_neg.iloc[1::4, :]
    Combineit_neg_3 = Combineit_neg.iloc[2::4, :]
    Combineit_neg_4 = Combineit_neg.iloc[3::4, :]

    invested_money = 100

    def calculate_final_investment_value(df):
        initial_investment = invested_money/4
        current_investment = initial_investment
        investment_values = []

        for index, row in df.iterrows():
            current_investment *= (1 + row['midquote'])
            investment_values.append(current_investment)

        return current_investment, investment_values

    # Assuming Combineit_neg_1, Combineit_neg_2, Combineit_neg_3, and Combineit_neg_4 are your DataFrames
    dataframes = [Combineit_neg_1, Combineit_neg_2, Combineit_neg_3, Combineit_neg_4]

    # Iterate over each DataFrame and calculate the final investment value
    for i, df in enumerate(dataframes, start=1):
        final_value, _ = calculate_final_investment_value(df)
        #print(f"Final investment value for Combineit_neg_{i}: {final_value:.8f}")

    # and sum the final investment values
    final_investment_value = sum([calculate_final_investment_value(df)[0] for df in dataframes])
    print(f"Sum of final investment values: {final_investment_value:.8f}")

    print(f'Money earned by investing {invested_money} on strategy: {final_investment_value - invested_money:.8f}')
    print(f'Return on negative investment: {((final_investment_value - invested_money) / invested_money)*100:.8f}%')


    # save the return on negative investment to the excel_df
    excel_df.loc['Return on short investment only (based on optimal short threshold only) for the optimization for Return', selected_time] = ((final_investment_value - invested_money) / invested_money)*100


    from sklearn.metrics import roc_auc_score, roc_curve, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Assuming test_df['midquote_target'] and test_df['predicted_return'] are already defined

    # Calculate AUC-ROC
    auc_roc = roc_auc_score(test_df['midquote_target'], test_df['predicted_return'])
    print(f"AUC-ROC: {auc_roc:.4f}")

    # Generate ROC curve data
    fpr, tpr, thresholds = roc_curve(test_df['midquote_target'], test_df['predicted_return'])

    # Plot ROC curve
    plt.figure(figsize=(8, 8))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % auc_roc)
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    #plt.title('Receiver Operating Characteristic')
    plt.legend(loc="lower right")
    # save the picture to a file
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/ROC_curve{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')
    #plt.show()

    # Performance Metrics
    precision = precision_score(test_df['midquote_target'], test_df['predicted_return'] > 0.5)
    recall = recall_score(test_df['midquote_target'], test_df['predicted_return'] > 0.5)
    f1 = f1_score(test_df['midquote_target'], test_df['predicted_return'] > 0.5)
    accuracy = accuracy_score(test_df['midquote_target'], test_df['predicted_return'] > 0.5)

    print(f"Accuracy: {accuracy:.6f}")
    print(f"Precision: {precision:.6f}")
    print(f"Recall: {recall:.6f}")
    print(f"F1 Score: {f1:.6f}")

    # save the metrics to the excel_df
    excel_df.loc['AUC-ROC', selected_time] = auc_roc
    excel_df.loc['Accuracy', selected_time] = accuracy
    excel_df.loc['Precision', selected_time] = precision
    excel_df.loc['Recall', selected_time] = recall
    excel_df.loc['F1 Score', selected_time] = f1


    # Calculating Confusion Matrix
    conf_matrix = confusion_matrix(test_df['midquote_target'], test_df['predicted_return'] > 0.5)
    tn, fp, fn, tp = conf_matrix.ravel()

    # Plotting the Confusion Matrix
    plt.figure(figsize=(8, 8))
    sns.heatmap(conf_matrix, annot=True, fmt="d", cmap='Blues', square=True,
                xticklabels=['0', '1'], yticklabels=['0', '1'],annot_kws={"size": 16})
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.xlabel('Predicted Label', fontsize=16)
    plt.ylabel('True Label', fontsize=16)
    #plt.title(f'Confusion Matrix for the {selected_time} Seconds Model', fontsize=16)
    
    # save the picture to a file
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/confusion_matrix{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')
    #plt.show()


    def calculate_combined_for_best(x, df):
        selected_stocks = x

        # Assuming df is your original DataFrame

        # Step 1: Indices for the two smallest
        smallest_indices = df.groupby('Time')['predicted_return'].nsmallest(selected_stocks).index.get_level_values(1)

        # Creating a copy for manipulation
        modified_df = df.copy()

        # Step 2: Change midquote values to negative for smallest_indices
        modified_df.loc[smallest_indices, 'midquote'] = -modified_df.loc[smallest_indices, 'midquote']

        # Now, proceed with the selection of largest and smallest but using modified_df for smallest
        # Step 3: Indices for the two largest
        largest_indices = df.groupby('Time')['predicted_return'].nlargest(selected_stocks).index.get_level_values(1)

        # Combining indices from the original and modified DataFrames
        combined_indices = largest_indices.union(smallest_indices)

        # Selecting combined indices from both modified and original DataFrames
        # Note: For largest indices, we use the original DataFrame to keep their values unchanged
        filtered_df = pd.concat([
            df.loc[largest_indices],
            modified_df.loc[smallest_indices]
        ])

        #sort the dataframe
        filtered_df = filtered_df.sort_values(by='Time')

        # Steps 4-6: Calculate mean and standard deviation of midquote, then compute Sharpe ratio
        mean_per_time = filtered_df.groupby('Time')['midquote'].mean()
        overall_mean = mean_per_time.mean()
        overall_std = mean_per_time.std()

        sharpe_ratio = overall_mean / overall_std

        return(sharpe_ratio)


    def calculate_positive_for_best(x, df):
        selected_stocks = x

        # Now, proceed with the selection of largest and smallest but using modified_df for smallest
        # Step 3: Indices for the two largest
        largest_indices = df.groupby('Time')['predicted_return'].nlargest(selected_stocks).index.get_level_values(1)

        # Combining indices from the original and modified DataFrames
        combined_indices = largest_indices

        filtered_df = df.loc[largest_indices]

        #sort the dataframe
        filtered_df = filtered_df.sort_values(by='Time')

        # Steps 4-6: Calculate mean and standard deviation of midquote, then compute Sharpe ratio
        mean_per_time = filtered_df.groupby('Time')['midquote'].mean()
        overall_mean = mean_per_time.mean()
        overall_std = mean_per_time.std()

        sharpe_ratio = overall_mean / overall_std

        return(sharpe_ratio)


    def calculate_negative_for_best(x, df):
        selected_stocks = x

        # Assuming df is your original DataFrame

        # Step 1: Indices for the two smallest
        smallest_indices = df.groupby('Time')['predicted_return'].nsmallest(selected_stocks).index.get_level_values(1)

        # Creating a copy for manipulation
        modified_df = df.copy()

        # Step 2: Change midquote values to negative for smallest_indices
        modified_df.loc[smallest_indices, 'midquote'] = -modified_df.loc[smallest_indices, 'midquote']


        # Selecting combined indices from both modified and original DataFrames
        # Note: For largest indices, we use the original DataFrame to keep their values unchanged
        filtered_df = modified_df.loc[smallest_indices]

        #sort the dataframe
        filtered_df = filtered_df.sort_values(by='Time')

        # Steps 4-6: Calculate mean and standard deviation of midquote, then compute Sharpe ratio
        mean_per_time = filtered_df.groupby('Time')['midquote'].mean()
        overall_mean = mean_per_time.mean()
        overall_std = mean_per_time.std()

        sharpe_ratio = overall_mean / overall_std

        return(sharpe_ratio)


    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt


    # Define the range of x values to test
    x_values = range(1,41)  # Adjust this based on your DataFrame's characteristics

    # Initialize a list to store results
    results = []

    # Iterate over each x value
    for x in x_values:
        sharpe_ratio = calculate_combined_for_best(x, val_df)
        results.append((x, sharpe_ratio))

    # Convert results to a DataFrame for easier manipulation and visualization
    results_df = pd.DataFrame(results, columns=['x', 'Sharpe Ratio'])

    # Identify the optimal x value
    optimal_x_combined = results_df.loc[results_df['Sharpe Ratio'].idxmax()]

    print(f"Optimal x value: {optimal_x_combined['x']} with Sharpe Ratio: {optimal_x_combined['Sharpe Ratio']}")

    # Visualization
    plt.figure(figsize=(20, 10))
    plt.plot(results_df['x'], results_df['Sharpe Ratio'], marker='o', linestyle='-')
    #plt.title(f'Validation of Sharpe Ratio by Number of Selected Stocks for the Combined Strategy for the {selected_time} Seconds Model', fontsize=10)
    plt.xlabel('Number of Selected Stocks', fontsize=16)
    plt.ylabel('Sharpe Ratio', fontsize=16)
    plt.xticks(size=14)
    plt.yticks(size=14)
    plt.grid(True)
    # save the picture to a file
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/validation_for_strategy_with_x_stocks_each_time_on_both_sides_sharpe_ratio{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')
    #plt.show()


    # save the optimal x value to the excel_df
    excel_df.loc['Optimal x value for validation for the strategy with x on both sides on optimization for Sharpe Ratio', selected_time] = optimal_x_combined['x']
    excel_df.loc['Sharpe Ratio for validation for the strategy with x on both sides on optimization for Sharpe Ratio', selected_time] = optimal_x_combined['Sharpe Ratio']

    calculate_combined_for_best(optimal_x_combined['x'].astype(int),test_df)

    # save the results to the excel_df
    excel_df.loc['Best Sharpe Ratio for test data for combined based on strategy with x on both sides on the optimization for Sharpe Ratio', selected_time] = calculate_combined_for_best(optimal_x_combined['x'].astype(int),test_df)

    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt


    # Define the range of x values to test
    x_values = range(1, 41)  # Adjust this based on your DataFrame's characteristics

    # Initialize a list to store results

    results = []
    for x in x_values:
    # Iterate over each x value

        sharpe_ratio = calculate_positive_for_best(x, val_df)
        results.append((x, sharpe_ratio))

    # Convert results to a DataFrame for easier manipulation and visualization
    results_df = pd.DataFrame(results, columns=['x', 'Sharpe Ratio'])

    # Identify the optimal x value
    optimal_x_positive = results_df.loc[results_df['Sharpe Ratio'].idxmax()]

    print(f"Optimal x value: {optimal_x_positive['x']} with Sharpe Ratio: {optimal_x_positive['Sharpe Ratio']}")
    plt.figure(figsize=(20, 10))
    plt.plot(results_df['x'], results_df['Sharpe Ratio'], marker='o', linestyle='-')
    #plt.title(f'Validation of Sharpe Ratio by Number of Selected Stocks for the Long Strategy for the {selected_time} Seconds Model', fontsize=10)
    plt.xlabel('Number of Selected Stocks', fontsize=16)
    plt.ylabel('Sharpe Ratio', fontsize=16)
    plt.xticks(size=14)
    plt.yticks(size=14)
    plt.grid(True)

    plt.grid(True)
    # save the picture to a file
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/validation_for_long_strategy_only_with_x_stocks_each_time_sharpe_ratio{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')

    #plt.show()
    # save the optimal x value to the excel_df


    excel_df.loc['Optimal x value for validation for the long strategy only for strategy where we go long x each timestep on the optimization for Sharpe Ratio', selected_time] = optimal_x_positive['x']
    excel_df.loc['Sharpe Ratio for validation for the long strategy only for strategy where we go long x each timestep on the optimization for Sharpe Ratio', selected_time] = optimal_x_positive['Sharpe Ratio']



    calculate_positive_for_best(optimal_x_positive['x'].astype(int),test_df)


    # save the results to the excel_df
    excel_df.loc['Best Sharpe Ratio for test data for long based on strategy where we go long x each timestep on the optimization for Sharpe Ratio', selected_time] = calculate_positive_for_best(optimal_x_positive['x'].astype(int),test_df)


    import numpy as np
    import matplotlib.pyplot as plt# Assuming calculate_negative_for_best and val_df are defined elsewhere


    # Define the range of x values to test
    x_values = range(1, 41)  # Adjust this based on your DataFrame's characteristics

    # Initialize a list to store results
    results = []
    # Iterate over each x value
    for x in x_values:
        try:
            sharpe_ratio = calculate_negative_for_best(x, val_df)
            # Check if the sharpe_ratio is NaN or infinite, which can happen if overall_std is 0
            if np.isnan(sharpe_ratio) or np.isinf(sharpe_ratio):
                sharpe_ratio = 0  # or np.nan, depending on how you want to handle this case
        except ZeroDivisionError:
            sharpe_ratio = 0  # or np.nan, depending on how you want to handle this case
        results.append((x, sharpe_ratio))

    # Convert results to a DataFrame for easier manipulation and visualization
    results_df = pd.DataFrame(results, columns=['x', 'Sharpe Ratio'])

    # Identify the optimal x value
    optimal_x_negative = results_df.loc[results_df['Sharpe Ratio'].idxmax()]

    print(f"Optimal x value: {optimal_x_negative['x']} with Sharpe Ratio: {optimal_x_negative['Sharpe Ratio']}")
    plt.figure(figsize=(20, 10))
    plt.plot(results_df['x'], results_df['Sharpe Ratio'], marker='o', linestyle='-')
    #plt.title(f'Validation of Sharpe Ratio by Number of Selected Stocks for the Long Strategy for the {selected_time} Seconds Model', fontsize=10)
    plt.xlabel('Number of Selected Stocks', fontsize=16)
    plt.ylabel('Sharpe Ratio', fontsize=16)
    plt.xticks(size=14)
    plt.yticks(size=14)
    plt.grid(True)
    # save the picture to a file
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/validation_for_short_strategy_only_with_x_stocks_each_time_sharpe_ratio{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')
    #plt.show()


    excel_df.loc['Optimal x value for validation for the short strategy only for strategy where we go short x each timestep on the optimization for Sharpe Ratio', selected_time] = optimal_x_negative['x']
    excel_df.loc['Sharpe Ratio for validation for the short strategy only for strategy where we go short x each timestep on the optimization for Sharpe Ratio', selected_time] = optimal_x_negative['Sharpe Ratio']

    calculate_negative_for_best(optimal_x_negative['x'].astype(int),test_df)

    # save the results to the excel_df
    excel_df.loc['Best Sharpe Ratio for test data for short based on strategy where we go short x each timestep on the optimization for Sharpe Ratio', selected_time] = calculate_negative_for_best(optimal_x_negative['x'].astype(int),test_df)

    def calculate_combined_for_best_result(x, df):
        selected_stocks = x

        # Assuming df is your original DataFrame

        # Step 1: Indices for the two smallest
        smallest_indices = df.groupby('Time')['predicted_return'].nsmallest(selected_stocks).index.get_level_values(1)

        # Creating a copy for manipulation
        modified_df = df.copy()

        # Step 2: Change midquote values to negative for smallest_indices
        modified_df.loc[smallest_indices, 'midquote'] = -modified_df.loc[smallest_indices, 'midquote']    # Now, proceed with the selection of largest and smallest but using modified_df for smallest


        # Step 3: Indices for the two largest
        largest_indices = df.groupby('Time')['predicted_return'].nlargest(selected_stocks).index.get_level_values(1)

        # Combining indices from the original and modified DataFrames
        combined_indices = largest_indices.union(smallest_indices)
        # Note: For largest indices, we use the original DataFrame to keep their values unchanged
        # Selecting combined indices from both modified and original DataFrames
        filtered_df = pd.concat([
            df.loc[largest_indices],
            modified_df.loc[smallest_indices]
            ])
        #sort the dataframe
        filtered_df = filtered_df.sort_values(by='Time')
        mean_per_time = filtered_df.groupby('Time')['midquote'].mean()
        # Steps 4-6: Calculate mean and standard deviation of midquote, then compute Sharpe ratio

        overall_mean = mean_per_time.mean()
        overall_std = mean_per_time.std()    
        sharpe_ratio = overall_mean / overall_std


        return(filtered_df)


    df_tottenham = calculate_combined_for_best_result(optimal_x_combined['x'].astype(int), test_df)
    # Testing

    # Now you can safely modify df_tottenham without worrying about affecting test_df
    df_tottenham['correct_prediction'] = ((df_tottenham['predicted_return'] >= 0.5) & (df_tottenham['midquote_target'] >= 0.5)) | ((df_tottenham['predicted_return'] < 0.5) & (df_tottenham['midquote_target'] < 0.5))# Calculate and print the overall accuracy


    overall_accuracy = df_tottenham['correct_prediction'].mean()
    print(f"Overall Accuracy Score: {overall_accuracy:.4f}")

    # save the results to the excel_df
    excel_df.loc['Overall Accuracy Score for the combined strategy for the optimization for Sharpe Ratio for the strategy where we bo long/short x times each timestep', selected_time] = overall_accuracy


    import matplotlib.pyplot as plt

    import matplotlib.dates as mdates
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt

    # Assuming df_tottenham and selected_time are already defined
    # Assuming time_dict is defined

    # Group data by 'Time' and 'correct_prediction' to count occurrences
    prediction_counts = df_tottenham.groupby(['Time', 'correct_prediction']).size().unstack(fill_value=0)

    prediction_counts.columns = prediction_counts.columns.map({True: 'Correct Prediction', False: 'Incorrect Prediction'})

    # Reset index to make 'Time' a column again (useful for seaborn plotting)
    prediction_counts.reset_index(inplace=True)
    # Convert the Time column to datetime
    prediction_counts['Time'] = pd.to_datetime(prediction_counts['Time'])

    # Create a date range from the first to the last timestamp with 1-second intervals
    date_range = pd.date_range(start=prediction_counts['Time'].min(), end=prediction_counts['Time'].max(), freq=time_dict[selected_time])

    prediction_counts.set_index('Time', inplace=True)
    prediction_counts_complete = prediction_counts.reindex(date_range, fill_value=0).reset_index()
    prediction_counts_complete.rename(columns={'index': 'Time'}, inplace=True)

    # Make a moving average for the prediction_counts_complete for the incorrect and correct prediction columns
    prediction_counts_complete['correct_prediction_moving_average'] = prediction_counts_complete['Correct Prediction'].rolling(window=200).mean()
    prediction_counts_complete['incorrect_prediction_moving_average'] = prediction_counts_complete['Incorrect Prediction'].rolling(window=200).mean()

    # Remove the first 200 rows 
    prediction_counts_complete = prediction_counts_complete[200:]

    # Set the overall aesthetics
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(20, 10))

    # Plot the time series for moving averages
    sns.lineplot(data=prediction_counts_complete, x='Time', y='correct_prediction_moving_average', label='Correct Predictions (MA)', color='seagreen')
    sns.lineplot(data=prediction_counts_complete, x='Time', y='incorrect_prediction_moving_average', label='Incorrect Predictions (MA)', color='salmon')

    plt.ylabel('Number of Trades (MA=200)', fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=14)
    plt.legend(loc='upper left', fontsize=14, title='Prediction Types')
    plt.xlabel('')  # Remove x-axis label
    plt.grid(True, linestyle='--', linewidth=0.5)  # Lighter grid lines

    # Formatter for the x-axis based on selected time intervals
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter(str(x_dict[selected_time])))

    plt.tight_layout()

    # Save the picture to a file
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/accuracy_over_time_combined_for_strategy_with_fixed_number_of_trades_per_time_on_both_sides{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')



    #plt.show()

    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    # Assuming df_tottenham, best_x, best_y, selected_time, and time_dict are defined
    best_x = 0.5
    best_y = 0.5

    # Count the number of predictions above and below the thresholds
    above_threshold_counts = df_tottenham[df_tottenham['predicted_return'] >= best_x].groupby('Ticker').size()
    below_threshold_counts = df_tottenham[df_tottenham['predicted_return'] <= best_y].groupby('Ticker').size()

    # Calculate the average spread above and below the thresholds
    average_spread_above = df_tottenham[df_tottenham['predicted_return'] >= best_x].groupby('Ticker')['spread'].mean()
    average_spread_below = df_tottenham[df_tottenham['predicted_return'] <= best_y].groupby('Ticker')['spread'].mean()

    # Total counts and sorted tickers
    tickers = df_tottenham['Ticker'].unique()
    total_counts = above_threshold_counts.add(below_threshold_counts, fill_value=0)
    sorted_tickers = total_counts.sort_values(ascending=False).index

    # Reindexing to ensure all data aligns properly
    above_threshold_counts = above_threshold_counts.reindex(sorted_tickers, fill_value=0)
    below_threshold_counts = below_threshold_counts.reindex(sorted_tickers, fill_value=0)
    average_spread_above = average_spread_above.reindex(sorted_tickers, fill_value=np.nan)
    average_spread_below = average_spread_below.reindex(sorted_tickers, fill_value=np.nan)

    # Creating the figure and primary axis for the bar chart
    fig, ax1 = plt.subplots(figsize=(20, 10))
    ind = np.arange(len(sorted_tickers))

    # Plotting the bar charts for above and below threshold predictions
    ax1.bar(ind, below_threshold_counts, color='red', label='Short Strategy'.format(best_y))
    ax1.bar(ind, above_threshold_counts, bottom=below_threshold_counts, color='green', label='Long Strategy'.format(best_x))

    # Creating a secondary y-axis for the average spreads
    ax2 = ax1.twinx()

    # Scatter plots for the average spreads
    ax2.scatter(ind, average_spread_below, color='darkred', alpha=0.5, label='Average Spread for Short')
    ax2.scatter(ind, average_spread_above, color='darkgreen', alpha=0.5, label='Average Spread for Long')

    # Calculating and plotting lines of best fit for average spreads
    z_below = np.polyfit(ind[~np.isnan(average_spread_below)], average_spread_below.dropna(), 1)
    p_below = np.poly1d(z_below)
    ax2.plot(ind, p_below(ind), 'r--', alpha=0.75)

    z_above = np.polyfit(ind[~np.isnan(average_spread_above)], average_spread_above.dropna(), 1)
    p_above = np.poly1d(z_above)
    ax2.plot(ind, p_above(ind), 'g--', alpha=0.75)

    # Setting labels, ticks, legends, and formatting
    ax1.set_xticks(ind)
    ax1.set_xticklabels(sorted_tickers, rotation=90, fontsize=8)
    ax1.set_ylabel('Number of Predictions', fontsize=18)
    ax2.set_ylabel('Average Spread', fontsize=18)

    # Adjusting tick label size
    #ax1.tick_params(axis='x', labelsize=8)  # Set fontsize for x-axis ticks
    ax1.tick_params(axis='y', labelsize=14)  # Set fontsize for y-axis ticks
    ax2.tick_params(axis='y', labelsize=14)  # Set fontsize for secondary y-axis ticks

    ax1.legend(loc='upper left', fontsize=18)
    ax2.legend(loc='upper right', fontsize=18)

    ax1.grid(False)
    ax2.grid(False)
    ax1.set_xlim(left=-0.5, right=len(sorted_tickers)-0.5)

    fig.tight_layout()

    # Save the picture to a file
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/number_of_trades_and_average_spread_per_ticker_by_threshold_for_straetgy_with_fixed_trades{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')


    import matplotlib.pyplot as plt
    import seaborn as sns

    # Assuming `high_conf_pos` is prepared as before# Plotting the spread vs. midquote


    plt.figure(figsize=(20, 10))
    sns.scatterplot(data=df_tottenham, x='spread', y='midquote', hue='predicted_return', palette='coolwarm', alpha=0.5)

    #rename the box with the legend
    plt.legend(title='Predicted Return', loc='upper right')
    #plt.title(f'Spread vs. Return based on the Predicted Return for the Combined Strategy for the the {selected_time} Second Model ', fontsize=16)


    plt.xlabel('Spread')
    plt.ylabel('Return')

    #plt.show()
    from sklearn.metrics import roc_auc_score, roc_curve, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score


    import matplotlib.pyplot as plt
    import seaborn as sns

    # Assuming df_tottenham['midquote_target'] and df_tottenham['predicted_return'] are already defined# Calculate AUC-ROC


    auc_roc = roc_auc_score(df_tottenham['midquote_target'], df_tottenham['predicted_return'])
    print(f"AUC-ROC: {auc_roc:.4f}")

    # Generate ROC curve data
    fpr, tpr, thresholds = roc_curve(df_tottenham['midquote_target'], df_tottenham['predicted_return'])# Plot ROC curve


    plt.figure(figsize=(8, 8))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % auc_roc)
    plt.xlim([0.0, 1.0])
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylim([0.0, 1.0])
    #plt.title('Receiver Operating Characteristic')
    plt.ylabel('True Positive Rate')
    plt.legend(loc="lower right")
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/roc_curve_and_performance_metrics_for_combined_strategy_for_the_fixed_strategy_setup{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')
    #plt.show()# Performance Metrics

    recall = recall_score(df_tottenham['midquote_target'], df_tottenham['predicted_return'] > 0.5)
    precision = precision_score(df_tottenham['midquote_target'], df_tottenham['predicted_return'] > 0.5)

    f1 = f1_score(df_tottenham['midquote_target'], df_tottenham['predicted_return'] > 0.5)
    accuracy = accuracy_score(df_tottenham['midquote_target'], df_tottenham['predicted_return'] > 0.5)
    print(f"Precision: {precision:.6f}")
    print(f"Accuracy: {accuracy:.6f}")

    print(f"Recall: {recall:.6f}")
    print(f"F1 Score: {f1:.6f}")


    excel_df.loc['AUC-ROC for the combined strategy for the optimization for Sharpe Ratio for the fixed trades strategy', selected_time] = auc_roc
    # save the results to the excel_df
    excel_df.loc['Precision for the combined strategy for the optimization for Sharpe Ratio for the fixed trades strategy', selected_time] = precision
    excel_df.loc['Accuracy for the combined strategy for the optimization for Sharpe Ratio for the fixed trades strategy', selected_time] = accuracy

    excel_df.loc['Recall for the combined strategy for the optimization for Sharpe Ratio for the fixed trades strategy', selected_time] = recall
    excel_df.loc['F1 Score for the combined strategy for the optimization for Sharpe Ratio for the fixed trades strategy', selected_time] = f1# Calculating Confusion Matrix

    conf_matrix = confusion_matrix(df_tottenham['midquote_target'], df_tottenham['predicted_return'] > 0.5)
    tn, fp, fn, tp = conf_matrix.ravel()
    plt.figure(figsize=(8, 8))
    # Plotting the Confusion Matrix
    sns.heatmap(conf_matrix, annot=True, fmt="d", cmap='Blues', square=True,
            xticklabels=['0', '1'], yticklabels=['0', '1'],annot_kws={"size": 16})
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.xlabel('Predicted Label', fontsize=16)
    plt.ylabel('True Label', fontsize=16)

    #plt.title('Confusion Matrix')
    # save the picture to a file
    plt.savefig(f'/Users/jensknudsen/Desktop/result/{selected_time}/overleaf/confusion_matrix_for_combined_strategy_for_the_fixed_strategy_setup{time_dict[selected_time]}.png',dpi=300, bbox_inches='tight')
    #plt.show()

    # Calculate the distribution of 0s and 1s in the midquote_target column
    distribution = label_df_new['midquote_target'].value_counts()
    a =(distribution[0])/(distribution[0]+distribution[1])
    b = (distribution[1])/(distribution[0]+distribution[1])
    print('fordelingen:')
    print(f'0: {a:.4f}')
    print(f'1: {b:.4f}')

    # save the result
    excel_df.loc['Distibution of the whole test data set that is 0', selected_time] = a
    excel_df.loc['Distibution of the whole test data set that is 1', selected_time] = b

    # Calculate the distribution of 0s and 1s in the midquote_target column
    distribution = val_df['midquote_target'].value_counts()
    a =(distribution[0])/(distribution[0]+distribution[1])
    b = (distribution[1])/(distribution[0]+distribution[1])
    print('fordelingen:')
    print(f'0: {a:.4f}')
    print(f'1: {b:.4f}')

    # save the result
    excel_df.loc['Distibution of the validation data set that is 0', selected_time] = a
    excel_df.loc['Distibution of the validation data set that is 1', selected_time] = b

    # Calculate the distribution of 0s and 1s in the midquote_target column
    distribution = test_df['midquote_target'].value_counts()
    a =(distribution[0])/(distribution[0]+distribution[1])
    b = (distribution[1])/(distribution[0]+distribution[1])
    print('fordelingen:')
    print(f'0: {a:.4f}')
    print(f'1: {b:.4f}')

    #save the result
    excel_df.loc['Distibution of the test data set that is 0', selected_time] = a
    excel_df.loc['Distibution of the test data set that is 1', selected_time] = b


    print(f'Done with {selected_time} seconds')

# save the excel_df to a excel file
excel_df.to_excel('/Users/jensknudsen/Desktop/result/overleaf.xlsx')


# N.B. TRY AND TEST IF THE SR IS ALREADY STANDARDIZED OR IS IT CORRECT TO DO IT
standardized_dict = {'0,01': 25, '0,1': 2.5, '0,5': 1/2, '1': 1/4, '5': 1/20, '10': 1/40}
# for the long threshold model
import pandas as pd

# import the dataframe
df = pd.read_excel('/Users/jensknudsen/Desktop/result/overleaf.xlsx', index_col=False)

# Threshold strategy (long only)
df = df.iloc[3:7]

new_columns = ['SR for Long (val)', 'Threshold for long (val)', 'SR for Long(test)', 'ACC for long (test)']
df.index = new_columns

df = df.transpose()
# delete the first row
df = df.iloc[1:]

df['SR for Long Std. (1 sec) (test)'] = df.apply(lambda row: row['SR for Long(test)'] * math.sqrt(standardized_dict[row.name]), axis=1)

# make the last column the second last column
cols = df.columns.tolist()
# move the last column to the second last position
cols = cols[:-2] + [cols[-1]] + [cols[-2]]
df = df[cols]
# make the last column the first column
cols = [cols[-1]] + cols[:-1]
df = df[cols]
#mke the third column the first column
cols = [cols[2]] + cols[:2] + cols[3:]
df = df[cols]


formatters = {
    'Threshold for Long (val)': '{:0.4f}'.format,
    'ACC for Long (test)': '{:0.4f}'.format,
    'SR for Long (val)': '{:0.4f}'.format,
    'SR for Long(test)': '{:0.4f}'.format,
    'SR for Long Std. (1 sec) (test)': '{:0.4f}'.format
}


# Generate LaTeX code
latex_code = df.to_latex(caption="For the Long Threshold Model",
                         label="tab:long_threshold_model",
                         formatters=formatters)

# Add the [H] specifier to the table environment
latex_code = latex_code.replace(r'\begin{table}', r'\begin{table}[H]')

# Save the modified LaTeX code to a file
with open('/Users/jensknudsen/Desktop/result/overleaf/threshold_long_only.tex', 'w') as file:
    file.write(latex_code)

# for the Short threshold model
import pandas as pd

# import the dataframe
df = pd.read_excel('/Users/jensknudsen/Desktop/result/overleaf.xlsx', index_col=False)

# Threshold strategy (long only)
df = df.iloc[7:11]

new_columns = ['SR for Short (val)', 'Threshold for Short (val)', 'SR for Short(test)', 'ACC for Short (test)']
df.index = new_columns

df = df.transpose()

# delete the first row
df = df.iloc[1:]

df['SR for Short Std. (1 sec) (test)'] = df.apply(lambda row: row['SR for Short(test)'] * math.sqrt(standardized_dict[row.name]), axis=1)

# make the last column the second last column
cols = df.columns.tolist()
# move the last column to the second last position
cols = cols[:-2] + [cols[-1]] + [cols[-2]]
df = df[cols]
# make the last column the first column
cols = [cols[-1]] + cols[:-1]
df = df[cols]
#mke the third column the first column
cols = [cols[2]] + cols[:2] + cols[3:]
df = df[cols]


formatters = {
    'Threshold for Short (val)': '{:0.4f}'.format,
    'ACC for Short (test)': '{:0.4f}'.format,
    'SR for Short (val)': '{:0.4f}'.format,
    'SR for Short(test)': '{:0.4f}'.format,
    'SR for Short Std. (1 sec) (test)': '{:0.4f}'.format
}

# Generate LaTeX code
latex_code = df.to_latex(caption="For the Short Threshold Model",
                         label="tab:Short_threshold_model",
                         formatters=formatters)

# Add the [H] specifier to the table environment
latex_code = latex_code.replace(r'\begin{table}', r'\begin{table}[H]')

# Save the modified LaTeX code to a file
with open('/Users/jensknudsen/Desktop/result/overleaf/threshold_short_only.tex', 'w') as file:
    file.write(latex_code)


# Combined for thresholds
import pandas as pd

# import the dataframe
df = pd.read_excel('/Users/jensknudsen/Desktop/result/overleaf.xlsx', index_col=False)

df = df.iloc[11:16]
new_columns = ['SR for Comb. (val)', 'Up. Thr. for Comb. (val)','Lo. Thr. for Comb. (val)', 'SR for Comb.(test)', 'ACC for Comb. (test)']

df.index = new_columns


df = df.transpose()

# delete the first row
df = df.iloc[1:]

df['SR for Comb. Std. (1 sec) (test)'] = df.apply(lambda row: row['SR for Comb.(test)'] * math.sqrt(standardized_dict[row.name]), axis=1)

# make the second last column the first column
cols = df.columns.tolist()

#move the second last column to the first position
cols = [cols[-2]] + cols[:-2] + [cols[-1]]
df = df[cols]

# move the the 3 and 4 to the first and second column
cols = [cols[2]] + [cols[3]] + cols[:2] + cols[4:]
df = df[cols]



formatters = {
    'SR for Comb. (val)': '{:0.4f}'.format,
    'Up. Thr. for Comb. (val)': '{:0.4f}'.format,
    'Lo. Thr. for Comb. (val)': '{:0.4f}'.format,
    'SR for Comb.(test)': '{:0.4f}'.format,
    'ACC for Comb. (test)': '{:0.4f}'.format,
    'SR for Comb. Std. (1 sec) (test)': '{:0.4f}'.format
}

# Generate LaTeX code
latex_code = df.to_latex(caption="For the Comb. Threshold Model",
                         label="tab:Comb._threshold_model",
                         formatters=formatters)

# Add the [H] specifier to the table environment
latex_code = latex_code.replace(r'\begin{table}', r'\begin{table}[H]')

# Save the modified LaTeX code to a file
with open('/Users/jensknudsen/Desktop/result/overleaf/threshold_Comb._only.tex', 'w') as file:
    file.write(latex_code)

# Combined for thresholds
import pandas as pd

# import the dataframe
df = pd.read_excel('/Users/jensknudsen/Desktop/result/overleaf.xlsx', index_col=False)

df = df.iloc[20:23]


new_columns = ['Ret (Combined)', 'Ret (Long)', 'Ret (Short)']
df.index = new_columns

df = df.transpose()

# delete the first row
df = df.iloc[1:]

formatters = {
    'Ret (Combined)': '{:0.3f}'.format,
    'Ret (Long)': '{:0.3f}'.format,
    'Ret (Short)': '{:0.3f}'.format
}

# Generate LaTeX code
latex_code = df.to_latex(caption="Return Based on Threshold Strategy",
                         label="tab:Return_Based_on_Threshold_Strategy",
                         formatters=formatters)

# Add the [H] specifier to the table environment
latex_code = latex_code.replace(r'\begin{table}', r'\begin{table}[H]')

# Save the modified LaTeX code to a file
with open('/Users/jensknudsen/Desktop/result/overleaf/Return_Based_on_Threshold_Strategy.tex', 'w') as file:
    file.write(latex_code)

# Overall performance (whole test set)
import pandas as pd

# import the dataframe
df = pd.read_excel('/Users/jensknudsen/Desktop/result/overleaf.xlsx', index_col=False)

df = df.iloc[37:42]

new_columns = ['AUC-ROC', 'Accuracy', 'Precision','Recall','F1 Score']
df.index = new_columns

df = df.transpose()

# delete the first row
df = df.iloc[1:]

formatters = {
    'AUC-ROC': '{:0.3f}'.format,
    'Accuracy': '{:0.3f}'.format,
    'Precision': '{:0.3f}'.format,
    'Recall': '{:0.3f}'.format,
    'F1 Score': '{:0.3f}'.format
}

# Generate LaTeX code
latex_code = df.to_latex(caption="Metrics for the whole test set",
                         label="tab:Metrics_for_the_whole_test_set",
                         formatters=formatters)

# Add the [H] specifier to the table environment
latex_code = latex_code.replace(r'\begin{table}', r'\begin{table}[H]')

# Save the modified LaTeX code to a file
with open('/Users/jensknudsen/Desktop/result/overleaf/Metrics_for_the_whole_test_set.tex', 'w') as file:
    file.write(latex_code)


# Overall performance (for the fixed strategy only) 
import pandas as pd

# import the dataframe
df = pd.read_excel('/Users/jensknudsen/Desktop/result/overleaf.xlsx', index_col=False)

df = df.iloc[52:57]


new_columns = ['AUC-ROC', 'Accuracy', 'Precision','Recall','F1 Score']
df.index = new_columns

df = df.transpose()

# delete the first row
df = df.iloc[1:]

formatters = {
    'AUC-ROC': '{:0.3f}'.format,
    'Accuracy': '{:0.3f}'.format,
    'Precision': '{:0.3f}'.format,
    'Recall': '{:0.3f}'.format,
    'F1 Score': '{:0.3f}'.format
}

# Generate LaTeX code
latex_code = df.to_latex(caption="Metric for the Fixed Strategy Model",
                         label="tab:Metric_for_the_Fixed_Strategy_Model",
                         formatters=formatters)

# Add the [H] specifier to the table environment
latex_code = latex_code.replace(r'\begin{table}', r'\begin{table}[H]')

# Save the modified LaTeX code to a file
with open('/Users/jensknudsen/Desktop/result/overleaf/Metric_for_the_Fixed_Strategy_Model.tex', 'w') as file:
    file.write(latex_code)



# Overall performance (for the fixed strategy combined) 
import pandas as pd

# import the dataframe
df = pd.read_excel('/Users/jensknudsen/Desktop/result/overleaf.xlsx', index_col=False)


df = df.iloc[42:45]


new_columns = ['Opt. X (Val)', 'SR (Val)', 'SR (Test)']
df.index = new_columns

df = df.transpose()

# delete the first row
df = df.iloc[1:]

df['SR Std. (1 sec) (Test)'] = df.apply(lambda row: row['SR (Test)'] * math.sqrt(standardized_dict[row.name]), axis=1)

formatters = {
    'Opt. X (Val)': '{:0.0f}'.format,
    'SR (Val)': '{:0.3f}'.format,
    'SR (Test)': '{:0.3f}'.format,
    'SR Std. (1 sec) (Test)': '{:0.3f}'.format
}

# Generate LaTeX code
latex_code = df.to_latex(caption="SR for Combined Fixed Strategy Model",
                         label="tab:SR_for_Combined_Fixed_Strategy_Model",
                         formatters=formatters)

# Add the [H] specifier to the table environment
latex_code = latex_code.replace(r'\begin{table}', r'\begin{table}[H]')

# Save the modified LaTeX code to a file
with open('/Users/jensknudsen/Desktop/result/overleaf/SR_for_Combined_Fixed_Strategy_Model.tex', 'w') as file:
    file.write(latex_code)


# Overall performance (for the fixed strategy long) 
import pandas as pd

# import the dataframe
df = pd.read_excel('/Users/jensknudsen/Desktop/result/overleaf.xlsx', index_col=False)


df = df.iloc[45:48]


new_columns = ['Opt. X (Val)', 'SR (Val)', 'SR (Test)']
df.index = new_columns

df = df.transpose()

# delete the first row
df = df.iloc[1:]

df['SR Std. (1 sec) (Test)'] = df.apply(lambda row: row['SR (Test)'] * math.sqrt(standardized_dict[row.name]), axis=1)

formatters = {
    'Opt. X (Val)': '{:0.0f}'.format,
    'SR (Val)': '{:0.3f}'.format,
    'SR (Test)': '{:0.3f}'.format,
    'SR Std. (1 sec) (Test)': '{:0.3f}'.format
}

# Generate LaTeX code
latex_code = df.to_latex(caption="SR for Long Fixed Strategy Model",
                         label="tab:SR_for_Long_Fixed_Strategy_Model",
                         formatters=formatters)

# Add the [H] specifier to the table environment
latex_code = latex_code.replace(r'\begin{table}', r'\begin{table}[H]')

# Save the modified LaTeX code to a file
with open('/Users/jensknudsen/Desktop/result/overleaf/SR_for_Long_Fixed_Strategy_Model.tex', 'w') as file:
    file.write(latex_code)


# Overall performance (for the fixed strategy short) 
import pandas as pd

# import the dataframe
df = pd.read_excel('/Users/jensknudsen/Desktop/result/overleaf.xlsx', index_col=False)


df = df.iloc[48:51]


new_columns = ['Opt. X (Val)', 'SR (Val)', 'SR (Test)']
df.index = new_columns

df = df.transpose()

# delete the first row
df = df.iloc[1:]

df['SR Std. (1 sec) (Test)'] = df.apply(lambda row: row['SR (Test)'] * math.sqrt(standardized_dict[row.name]), axis=1)

formatters = {
    'Opt. X (Val)': '{:0.0f}'.format,
    'SR (Val)': '{:0.3f}'.format,
    'SR (Test)': '{:0.3f}'.format,
    'SR Std. (1 sec) (Test)': '{:0.3f}'.format
}

# Generate LaTeX code
latex_code = df.to_latex(caption="SR for Short Fixed Strategy Model",
                         label="tab:SR_for_Short_Fixed_Strategy_Model",
                         formatters=formatters)

# Add the [H] specifier to the table environment
latex_code = latex_code.replace(r'\begin{table}', r'\begin{table}[H]')

# Save the modified LaTeX code to a file
with open('/Users/jensknudsen/Desktop/result/overleaf/SR_for_Short_Fixed_Strategy_Model.tex', 'w') as file:
    file.write(latex_code)


# Overall performance (for the fixed strategy short) 
import pandas as pd

# import the dataframe
df = pd.read_excel('/Users/jensknudsen/Desktop/result/overleaf.xlsx', index_col=False)


df = df.iloc[57:63]


new_columns = ['0 (Test)', '1 (Test)', '0 (Test (sub))', '1 (Test (sub))', '0 (Val)', '1 (Val)']
df.index = new_columns

df = df.transpose()

# delete the first row
df = df.iloc[1:]

formatters = {
    '0 (Test)': '{:0.0f}'.format,
    '1 (Test)': '{:0.3f}'.format,
    '0 (Test (sub))': '{:0.3f}'.format,
    '1 (Test (sub))': '{:0.0f}'.format,
    '0 (Val)': '{:0.3f}'.format,
    '1 (Val)': '{:0.3f}'.format
}

# Generate LaTeX code
latex_code = df.to_latex(caption="Distribution of 0s and 1s in the Test and Validation Sets",
                         label="tab:Distribution_of_0s_and_1s_in_the_Test_and_Validation_Sets",
                         formatters=formatters)

# Add the [H] specifier to the table environment
latex_code = latex_code.replace(r'\begin{table}', r'\begin{table}[H]')

# Save the modified LaTeX code to a file
with open('/Users/jensknudsen/Desktop/result/overleaf/Distribution_of_0s_and_1s_in_the_Test_and_Validation_Sets.tex', 'w') as file:
    file.write(latex_code)


## COMBINING FILES INTO ONE FOLDER
#import shutil
#import os
#
## List of source folders
#source_folders = [
#    '/Users/jensknudsen/Desktop/result/0,01/overleaf',
#    '/Users/jensknudsen/Desktop/result/0,1/overleaf',
#    '/Users/jensknudsen/Desktop/result/0,5/overleaf',
#    '/Users/jensknudsen/Desktop/result/1/overleaf',
#    '/Users/jensknudsen/Desktop/result/5/overleaf',
#    '/Users/jensknudsen/Desktop/result/10/overleaf'
#]
#
## Destination folder
#destination_folder = '/Users/jensknudsen/Desktop/result/combined'
#
## Create the destination folder if it does not exist
#if not os.path.exists(destination_folder):
#    os.makedirs(destination_folder)
#
#
#
#for folder in source_folders:
#    for filename in os.listdir(folder):
#        source_path = os.path.join(folder, filename)
#        destination_path = os.path.join(destination_folder, filename)
#        
#        # Check if it's a file and not a directory
#        if os.path.isfile(source_path):
#            shutil.copy2(source_path, destination_path)

