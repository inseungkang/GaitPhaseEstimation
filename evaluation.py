import glob
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from data_processing import *
# from model_training import *
from data_cleaning import *

def convert_to_polar(gp):
    theta = gp * 2 * np.pi
    x = np.cos(theta)
    y = np.sin(theta)
    return x, y

def convert_to_gp(x, y):
    gp = np.mod(np.arctan2(y, x)+2*np.pi, 2*np.pi) / (2*np.pi)
    return gp

def calculate_truth_and_pred(data):
    l_x_true, l_y_true = label_vectors(data['leftJointPosition'])
    l_x_pred, l_y_pred = convert_to_polar(data['leftGaitPhase'])

    # r_x_true = r_y_true = r_x_pred = r_y_pred = pd.Series(0, index=data.index)
    r_x_true, r_y_true = label_vectors(data['rightJointPosition'])
    r_x_pred, r_y_pred = convert_to_polar(data['rightGaitPhase'])
    
    true = pd.concat([l_x_true, l_y_true, r_x_true, r_y_true], axis=1)
    true.columns = ['l_x_true', 'l_y_true', 'r_x_true', 'r_y_true']

    pred = pd.concat([l_x_pred, l_y_pred, r_x_pred, r_y_pred], axis=1)
    pred.columns = ['l_x_pred', 'l_y_pred', 'r_x_pred', 'r_y_pred']
    
    data = pd.concat([data, true, pred], axis=1)
    return data

def calculate_pred(data):
    # l_x_pred, l_y_pred = convert_to_polar(data['leftGaitPhase'])
    # r_x_pred, r_y_pred = convert_to_polar(data['rightGaitPhase'])
    
    pred = pd.concat([l_x_pred, l_y_pred, r_x_pred, r_y_pred], axis=1)
    pred.columns = ['l_x_pred', 'l_y_pred', 'r_x_pred', 'r_y_pred']
    
    data = pd.concat([data, pred], axis=1)
    return data

def cut_standing_phase(data, locomotionmode):
    l_data = r_data = data
    l_gp = convert_to_gp(data['leftGaitPhaseX'], data['leftGaitPhaseY'])
    lmaximas, _ = find_peaks(l_gp)
    lmaximas = list(lmaximas)
    l_stand_phase = list(data[data['leftWalkMode']==locomotionmode].index)
    l_stand_phase = np.split(l_stand_phase, np.where(np.diff(l_stand_phase) != 1)[0]+1)
    
    for phase in l_stand_phase:
        if len(phase) == 0:
            break
        # if phase[0] > lmaximas[0]:
        #     bf = min(lmaximas, key=lambda x : abs(x-phase[0]))
        #     if bf > phase[0]:
        #         bf = lmaximas[lmaximas.index(bf) - 2]
        # else: 
        #     bf = 0
        # if phase[-1] < lmaximas[-1]:
        #     af = min(lmaximas, key=lambda x : abs(x-phase[-1]))
        #     if af < phase[-1]:
        #         af = lmaximas[lmaximas.index(af) + 2]
        # else:
        #     af = data.shape[0]-1
        # l_data = l_data.drop(np.arange(bf, af), axis=0)
        l_data = l_data.drop(np.arange(phase[0], phase[-1]+1), axis=0)
    l_data = l_data.reset_index()
    
    r_gp = convert_to_gp(data['rightGaitPhaseX'], data['rightGaitPhaseY'])
    rmaximas, _ = find_peaks(r_gp)
    rmaximas = list(rmaximas)
    
    r_stand_phase = list(data[data['rightWalkMode']==locomotionmode].index)
    r_stand_phase = np.split(r_stand_phase, np.where(np.diff(r_stand_phase) != 1)[0]+1)
    for phase in r_stand_phase:
        if len(phase) == 0:
            break
        # if phase[0] > rmaximas[0]:
        #     bf = min(rmaximas, key=lambda x : abs(x-phase[0]))
        #     if bf > phase[0]:
        #         bf = rmaximas[rmaximas.index(bf) - 1]
        # else: 
        #     bf = 0
        # if phase[-1] < rmaximas[-1]:
        #     af = min(rmaximas, key=lambda x : abs(x-phase[-1]))
        #     if af < phase[-1]:
        #         af = rmaximas[rmaximas.index(af) + 1]
        # else:
        #     af = data.shape[0]-1
        # r_data = r_data.drop(np.arange(bf, af+1), axis=0)
        r_data = r_data.drop(np.arange(phase[0], phase[-1]+1), axis=0)
    r_data = r_data.reset_index()
    
    return l_data, r_data
   
def find_mode_transition_cycles(l_data, r_data):

    mode_diff = [0] + np.diff(l_data['leftWalkMode'])
    transitions = np.unique(mode_diff)
    transitions = transitions[transitions!=0]
    l_transition_cycles = {key:[] for key in transitions}
    mode_transition = [(i, v) for i, v in enumerate(mode_diff) if v != 0]
    l_gp = convert_to_gp(l_data['leftGaitPhaseX'], l_data['leftGaitPhaseY'])
    l_maximas, _ = find_peaks(l_gp)
    l_maximas = list(l_maximas)
    for point, v in mode_transition:
        closest = (min(l_maximas, key=lambda x : abs(x-point)))
        if closest >= point:
            l_transition_cycles[v].append((l_maximas[l_maximas.index(closest) - 1], closest))
        else:
            try:
                l_transition_cycles[v].append((closest , l_maximas[l_maximas.index(closest) + 1]))
            except:
                l_transition_cycles[v].append((l_maximas[l_maximas.index(closest) - 1], closest))
    # plt.vlines(list(l_transition_cycles.values()), -1.5, 0.5, 'y')
    plt.plot(l_gp, label='manual_ground_truth')
    # plt.plot(l_data['leftJointPosition'], label='Joint Position')
    plt.plot(l_data['leftGaitPhase'], alpha=0.7, label='predicted')
    plt.plot(l_data['leftWalkMode'], label='mode')
    plt.legend(loc=9)
    plt.show()

    mode_diff = [0] + np.diff(r_data['rightWalkMode'])
    transitions = np.unique(mode_diff)
    transitions = transitions[transitions!=0]
    r_transition_cycles = {key:[] for key in transitions}
    mode_transition = [(i, v) for i, v in enumerate(mode_diff) if v != 0]
    r_gp = convert_to_gp(r_data['rightGaitPhaseX'], r_data['rightGaitPhaseY'])
    r_maximas, _ = find_peaks(r_gp)
    r_maximas = list(r_maximas)
    for point, v in mode_transition:
        closest = (min(r_maximas, key=lambda x : abs(x-point)))
        if closest >= point:
            r_transition_cycles[v].append((r_maximas[r_maximas.index(closest) - 1], closest))
        else:
            r_transition_cycles[v].append((closest , r_maximas[r_maximas.index(closest) + 1]))
    # plt.vlines(r_transition_cycles[4], -1.5, 0.5, 'y')
    plt.plot(r_gp, label='manual_ground_truth')
    # plt.plot(r_data['rightJointPosition'], label='Joint Position')
    plt.plot(r_data['rightGaitPhase'], alpha=0.7, label='predicted')
    plt.plot(r_data['rightWalkMode'], label='mode')
    plt.legend(loc=9)
    plt.show()
    return l_transition_cycles, r_transition_cycles

def get_mse(y_true, y_pred):
    #Raw values and Prediction are in X,Y
    labels, theta, gp = {}, {}, {}

    #Separate legs
    left_true = y_true[:, :2]
    right_true = y_true[:, 2:]
    left_pred = y_pred[:, :2]
    right_pred = y_pred[:, 2:]
    
    #Calculate cosine distance
    left_num = np.sum(np.multiply(left_true, left_pred), axis=1)
    left_denom = np.linalg.norm(left_true, axis=1) * np.linalg.norm(left_pred, axis=1)
    right_num = np.sum(np.multiply(right_true, right_pred), axis=1)
    right_denom = np.linalg.norm(right_true, axis=1) * np.linalg.norm(right_pred, axis=1)

    left_cos = left_num / left_denom
    right_cos = right_num / right_denom
    
    #Clip large values and small values
    left_cos = np.minimum(left_cos, np.zeros(left_cos.shape)+1)
    left_cos = np.maximum(left_cos, np.zeros(left_cos.shape)-1)
    
    right_cos = np.minimum(right_cos, np.zeros(right_cos.shape)+1)
    right_cos = np.maximum(right_cos, np.zeros(right_cos.shape)-1)
    
    # What if denominator is zero (model predicts 0 for both X and Y)
    left_cos[np.isnan(left_cos)] = 0
    right_cos[np.isnan(right_cos)] = 0
    
    #Get theta error
    left_theta = np.arccos(left_cos)
    right_theta = np.arccos(right_cos)
    
    #Get gait phase error
    left_gp_error = left_theta * 100 / (2*np.pi)
    right_gp_error = right_theta * 100 / (2*np.pi)
    
    #Get mse
    left_mse = np.square(left_gp_error)
    right_mse = np.square(right_gp_error)
    
    return left_mse, right_mse

def custom_rmse(y_true, y_pred):
    #Raw values and Prediction are in X,Y
    labels, theta, gp = {}, {}, {}

    #Separate legs
    left_true = y_true[:, :2]
    right_true = y_true[:, 2:]
    left_pred = y_pred[:, :2]
    right_pred = y_pred[:, 2:]
    
    #Calculate cosine distance
    left_num = np.sum(np.multiply(left_true, left_pred), axis=1)
    left_denom = np.linalg.norm(left_true, axis=1) * np.linalg.norm(left_pred, axis=1)
    right_num = np.sum(np.multiply(right_true, right_pred), axis=1)
    right_denom = np.linalg.norm(right_true, axis=1) * np.linalg.norm(right_pred, axis=1)

    left_cos = left_num / left_denom
    right_cos = right_num / right_denom
    
    #Clip large values and small values
    left_cos = np.minimum(left_cos, np.zeros(left_cos.shape)+1)
    left_cos = np.maximum(left_cos, np.zeros(left_cos.shape)-1)
    
    right_cos = np.minimum(right_cos, np.zeros(right_cos.shape)+1)
    right_cos = np.maximum(right_cos, np.zeros(right_cos.shape)-1)
    
    # What if denominator is zero (model predicts 0 for both X and Y)
    left_cos[np.isnan(left_cos)] = 0
    right_cos[np.isnan(right_cos)] = 0
    
    #Get theta error
    left_theta = np.arccos(left_cos)
    right_theta = np.arccos(right_cos)
    
    #Get gait phase error
    left_gp_error = left_theta * 100 / (2*np.pi)
    right_gp_error = right_theta * 100 / (2*np.pi)
    
    #Get rmse
    left_rmse = np.sqrt(np.mean(np.square(left_gp_error)))
    right_rmse = np.sqrt(np.mean(np.square(right_gp_error)))

    #Separate legs
    labels['left_true'] = left_true
    labels['right_true'] = right_true
    labels['left_pred'] = left_pred
    labels['right_pred'] = right_pred

    for key, value in labels.items(): 
        #Convert to polar
        theta[key] = np.arctan2(value[:, 1], value[:, 0])
        
        #Bring into range of 0 to 2pi
        theta[key] = np.mod(theta[key] + 2*np.pi, 2*np.pi)

        #Interpolate from 0 to 100%
        gp[key] = 100*theta[key] / (2*np.pi)

    return left_rmse, right_rmse

def custom_rmse_uni(true, pred):
    #Raw values and Prediction are in X,Y
    labels, theta = {}, {}
    
    #Calculate cosine distance
    num = np.sum(np.multiply(true, pred), axis=1)
    denom = np.linalg.norm(true, axis=1) * np.linalg.norm(pred, axis=1)

    cos = num / denom
    
    #Clip large values and small values
    cos = np.minimum(cos, np.zeros(cos.shape)+1)
    cos = np.maximum(cos, np.zeros(cos.shape)-1)
    
    # What if denominator is zero (model predicts 0 for both X and Y)
    cos[np.isnan(cos)] = 0
    
    #Get theta error
    theta = np.arccos(cos)
    
    #Get gait phase error
    gp_error = theta * 100 / (2*np.pi)
    
    #Get rmse
    rmse = np.sqrt(np.mean(np.square(gp_error)))

    return rmse

def plot_gp(true_gp, pred_gp, title):
    plt.plot(true_gp, label="Ground Truth")
    plt.plot(pred_gp, label="Predicted")
    plt.legend()
    plt.title(title)
    plt.show()
    
############################### Evaluation Script ############################

# # Load Data
headers = pd.read_csv('data/evalData/headers.txt')

subject = 'ST08'
path = 'data/strokeData/' + subject + '/'
mode = 'RA'
filename = subject + '_' + mode + '_Final.txt'

# Mannually labeling data
data = pd.read_csv(path + filename, skiprows=1, sep=" ")
data = data.dropna(axis=1)
data.columns = headers.columns.str.replace(' ', '')
data = data.loc[:,~data.columns.duplicated()]
manual_label_data_eval(data, path+"labeled_"+filename)

data = pd.read_csv(path+"labeled_"+filename)
data = calculate_truth_and_pred(data)
l_data, r_data = cut_standing_phase(data, 0)
l_true_gp = convert_to_gp(l_data['l_x_true'], l_data['l_y_true'])
r_true_gp = convert_to_gp(r_data['r_x_true'], r_data['r_y_true'])
plot_gp(l_true_gp, l_data['leftGaitPhase'], 'Left ' + mode)
plot_gp(r_true_gp, r_data['rightGaitPhase'], 'Right ' + mode)

# l_data, _ = cut_standing_phase(l_data, 1)
# _, r_data = cut_standing_phase(r_data, 1)

# l_data, r_data = pd.concat([l_data, l_data_LG]), pd.concat([r_data, r_data_LG])

# l_x_pred, l_y_pred = convert_to_polar(l_data[:, -6])
# l_pred = np.concatenate([l_x_pred, l_y_pred], axis=1)
# l_label = l_data[:, -4:-2]
# l_rmse = custom_rmse_uni(l_label, l_pred)

# r_data = r_data.to_numpy()
# r_x_pred, r_y_pred = convert_to_polar(r_data[:, -5])
# r_pred = np.concatenate([r_x_pred, r_y_pred], axis=1)
# r_label = r_data[:, -2:]
# r_rmse = custom_rmse_uni(r_label, r_pred)

# rmse = np.mean([l_rmse, r_rmse])
# print("Left RMSE: ", l_rmse, " Right RMSE: " , r_rmse, " Mean: ", rmse)

# output = pd.DataFrame(columns=['model', 'locomotion_mode', 'step_rmse'])
# # For Labeled Data
# for file in sorted(glob.glob(path+f'chopped_AB{subject}*')):
#     data = np.loadtxt(file)
#     l_x_pred, l_y_pred = convert_to_polar(data[:, -6])
#     r_x_pred, r_y_pred = convert_to_polar(data[:, -5])
#     l_x_pred = l_x_pred.reshape(-1, 1)
#     l_y_pred = l_y_pred.reshape(-1, 1)
#     r_x_pred = r_x_pred.reshape(-1, 1)
#     r_y_pred = r_y_pred.reshape(-1, 1)
#     data = np.concatenate([data, l_x_pred, l_y_pred, r_x_pred, r_y_pred], axis=1)
#     rmse = custom_rmse(data[:, -8:-4],
#                        data[:, -4:])
#     rmse = np.mean([rmse[0], rmse[1]])
#     mode = file.split('_')[3:]
#     mode = '_'.join(mode)
#     model = file.split('_')[2]
#     current_output = {
#     'model': model,
#     'locomotion_mode': mode,
#     'step_rmse': rmse
#     }
#     output = output.append(current_output, ignore_index=True)
# # output.to_excel('mode_output.xlsx')
# plt.figure()
# plt.style.use('seaborn-paper')

# # Create Nan array used to provide white space between each mode
# nan = np.empty((60, 38))
# nan.fill(np.nan)
# # modes = {1:'LG', 2:'RA', 3:'RD', 4:'SA', 5:'SD'}
# torque = pd.read_excel(path+'torque_profile_scaled.xlsx')
# torque_tables = {
#     1: torque[torque['Locomotion Mode'] == 'LG'],
#     2: torque[torque['Locomotion Mode'] == 'RA'],
#     3: torque[torque['Locomotion Mode'] == 'RD'],
#     4: torque[torque['Locomotion Mode'] == 'SA'],
#     5: torque[torque['Locomotion Mode'] == 'SD']    
# }

# #!NOTE: Change the list to change the order of the graph!!!
# mode_list = ['LG', 'LG_RA', 'RA', 'RA_LG', 'LG_SD', 'SD', 'SD_LG', 'LG_SA', 'SA', 'SA_LG', 'LG_RD', 'RD', 'RD_LG']

# plt.subplot(211)
# data = np.empty((0, 39))
# indices = [0]
# # Append all the mode data together in order of the mode list
# ct = 0

# torque = []
# commanded_torque = []
# for mode in mode_list:
#     file = path + f'chopped_AB{subject}_ML_{mode}.txt'
#     new_data = np.loadtxt(file)
#     new_index = np.linspace(1+ct, 200+ct, new_data.shape[0]).reshape(-1, 1)
#     new_nan = np.append(nan, np.linspace(201+ct, 250+ct, nan.shape[0]).reshape(-1, 1), axis=1)
#     new_data = np.append(new_data, new_index, axis=1)
#     data = np.append(data, new_data, axis=0)
#     data = np.append(data, new_nan, axis=0)
#     indices.append(225+ct)

#     for pt in new_data:
#         # Calculate Torque
#         if mode == 'RA_LG':
#             cur_mode = pt[-8]
#             cur_gp = convert_to_gp(pt[-3], pt[-2])
#             commanded_torque = np.append(commanded_torque, pt[-13])
#         elif mode == 'RD_LG':
#             cur_mode = pt[-8]
#             cur_gp = convert_to_gp(pt[-3], pt[-2])
#             commanded_torque = np.append(commanded_torque, pt[-13])
#         else:
#             cur_mode = pt[-9]
#             cur_gp = convert_to_gp(pt[-5], pt[-4])
#             commanded_torque = np.append(commanded_torque, pt[-14])

#         cur_gp = cur_gp * 100
#         cur_torque_table = torque_tables[int(cur_mode)]
#         cur_gt_torque = np.interp(cur_gp, cur_torque_table['Gait Phase'], cur_torque_table['Joint Torque'])
#         torque = np.append(torque, cur_gt_torque)
    
#     torque = np.append(torque, nan[:,1])
#     commanded_torque = np.append(commanded_torque, nan[:,1])

#     ct += 250
#     mode_label = ' to '.join(mode.split('_'))
#     rmse = '{:.2f}'.format(output[(output['model'] == 'ML') & (output['locomotion_mode']==mode+'.txt')]['step_rmse'].values[0])
#     plt.text(indices[-1]-((indices[-1]-indices[-2])/2), 1.3, mode_label+'\n'+rmse, 
#              horizontalalignment='center', verticalalignment='center', fontsize=7)
    
# gp = convert_to_gp(data[:, -5], data[:, -4])

# plt.plot(data[:, -1], gp, 'dimgrey', label='ground_truth')
# plt.plot(data[:, -1], data[:, -7], 'tab:blue', alpha=0.9, label='predicted')
# # plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
# plt.vlines(indices[1:-1], 0, 1.5, 'black', linestyles='dashed')
# plt.tick_params(
#     axis='x',          # changes apply to the x-axis
#     which='both',      # both major and minor ticks are affected
#     bottom=False,      # ticks along the bottom edge are off
#     top=False,         # ticks along the top edge are off
#     labelbottom=False)
# plt.yticks(ticks=[0, 0.5, 1], labels=['0%', '50%', '100%'])
# plt.ylabel('Gait Phase Percentage')

# plt.subplot(212)
# plt.plot(data[:, -1], torque, 'dimgrey', label='ground truth')
# plt.plot(data[:, -1], commanded_torque, 'tab:blue', label='commanded')

# plt.vlines(indices[1:-1], 0, 1.5, 'black', linestyles='dashed')
# plt.tick_params(
#     axis='x',          # changes apply to the x-axis
#     which='both',      # both major and minor ticks are affected
#     bottom=False,      # ticks along the bottom edge are off
#     top=False,         # ticks along the top edge are off
#     labelbottom=False)
# plt.ylabel('Assistance Torque (N-m)')
# plt.show()

# plt.subplot(211)
# data = np.empty((0, 39))
# indices = [0]

# ##### TBE PLOT
# # Append all the mode data together in order of the mode list
# torque = []
# commanded_torque = []
# ct = 0
# for mode in mode_list:
#     file = path + f'chopped_AB{subject}_TBE_{mode}.txt'
#     new_data = np.loadtxt(file)
#     new_data = new_data[:, 1:]
#     new_index = np.linspace(1+ct, 200+ct, new_data.shape[0]).reshape(-1, 1)
#     new_nan = np.append(nan, np.linspace(201+ct, 250+ct, nan.shape[0]).reshape(-1, 1), axis=1)
#     new_data = np.append(new_data, new_index, axis=1)
#     data = np.append(data, new_data, axis=0)
#     data = np.append(data, new_nan, axis=0)
#     indices.append(225+ct)

#     for pt in new_data:
#         # Calculate Torque
#         if mode == 'RA_LG':
#             cur_mode = pt[-8]
#             cur_gp = convert_to_gp(pt[-3], pt[-2])
#             commanded_torque = np.append(commanded_torque, pt[-13])
#         elif mode == 'RD_LG':
#             cur_mode = pt[-8]
#             cur_gp = convert_to_gp(pt[-3], pt[-2])
#             commanded_torque = np.append(commanded_torque, pt[-13])
#         else:
#             cur_mode = pt[-9]
#             cur_gp = convert_to_gp(pt[-5], pt[-4])
#             commanded_torque = np.append(commanded_torque, pt[-14])

#         cur_gp = cur_gp * 100
#         cur_torque_table = torque_tables[int(cur_mode)]
#         cur_gt_torque = np.interp(cur_gp, cur_torque_table['Gait Phase'], cur_torque_table['Joint Torque'])
#         torque = np.append(torque, cur_gt_torque)
    
#     torque = np.append(torque, nan[:,1])
#     commanded_torque = np.append(commanded_torque, nan[:,1])

#     ct += 250
#     mode_label = ' to '.join(mode.split('_'))
#     rmse = '{:.2f}'.format(output[(output['model'] == 'TBE') & (output['locomotion_mode']==mode+'.txt')]['step_rmse'].values[0])
#     plt.text(indices[-1]-((indices[-1]-indices[-2])/2), 1.3, mode_label+'\n'+rmse, 
#              horizontalalignment='center', verticalalignment='center', fontsize=7)
    
# gp = convert_to_gp(data[:, -5], data[:, -4])
# plt.plot(data[:, -1], gp, 'dimgrey', label='ground_truth')
# plt.plot(data[:, -1], data[:, -7], 'tab:red', alpha=0.9, label='predicted')
# # plt.legend(loc=1)
# plt.vlines(indices[1:-1], 0, 1.5, 'black', linestyles='dashed')

# plt.tick_params(
#     axis='x',          # changes apply to the x-axis
#     which='both',      # both major and minor ticks are affected
#     bottom=False,      # ticks along the bottom edge are off
#     top=False,         # ticks along the top edge are off
#     labelbottom=False) # labels along the bottom edge are off
# plt.yticks(ticks=[0, 0.5, 1], labels=['0%', '50%', '100%'])
# plt.ylabel('Gait Phase Percentage')

# plt.subplot(212)
# plt.plot(data[:, -1], torque, 'dimgrey', label='ground truth')
# plt.plot(data[:, -1], commanded_torque, 'tab:red', label='commanded')

# plt.vlines(indices[1:-1], 0, 1.5, 'black', linestyles='dashed')
# plt.tick_params(
#     axis='x',          # changes apply to the x-axis
#     which='both',      # both major and minor ticks are affected
#     bottom=False,      # ticks along the bottom edge are off
#     top=False,         # ticks along the top edge are off
#     labelbottom=False)
# plt.ylabel('Assistance Torque (N-m)')
# plt.show()

# exit()

# # data = manual_segment_magnitudes(data, path + f'segmented_AB{subject}_{method}')
# # filename = path + f'segmented_AB{subject}_{method}'
# # data = pd.read_csv(filename)
# # add 4 ground truth columns and 4 prediction columns at the end of data
# data = calculate_pred(data)
# l_data, r_data = cut_standing_phase(data)
# l_mse, _ = get_mse(l_data.iloc[:, -9:-5].to_numpy(), 
#                    l_data.iloc[:, -4:].to_numpy())
# _, r_mse = get_mse(r_data.iloc[:, -9:-5].to_numpy(), 
#                    r_data.iloc[:, -4:].to_numpy())
# # plt.plot(l_mse, label='left mse')
# # plt.plot(r_mse, label='right mse', alpha=0.7)
# # plt.legend()
# # plt.show()

# l_gp = convert_to_gp(l_data['leftGaitPhaseX'], l_data['leftGaitPhaseY'])
# plt.plot(l_gp, label='ground_truth')
# # plt.plot(l_data['leftJointPosition'], label='Joint Position')
# plt.plot(l_data['leftGaitPhase'], alpha=0.7, label='predicted')
# plt.plot(l_data['leftWalkMode'], label='mode')
# plt.legend(loc=9)
# plt.show()

# r_gp = convert_to_gp(r_data['rightGaitPhaseX'], r_data['rightGaitPhaseY'])
# plt.plot(r_gp, label='manual_ground_truth')
# # plt.plot(l_data['rightJointPosition'], label='Joint Position')
# plt.plot(r_data['rightGaitPhase'], alpha=0.7, label='predicted')
# plt.plot(l_data['rightWalkMode'], label='mode')
# plt.legend(loc=9)

# plt.show()

# Calculate the overall rmse
l_overall_rmse = custom_rmse(l_data.iloc[:, -8:-4].to_numpy(), 
                             l_data.iloc[:, -4:].to_numpy())
r_overall_rmse = custom_rmse(r_data.iloc[:, -8:-4].to_numpy(), 
                             r_data.iloc[:, -4:].to_numpy())
overall_rmse = (l_overall_rmse[0], r_overall_rmse[1])
print(overall_rmse)
print((overall_rmse[0]+overall_rmse[1])/2)
exit()
# # Find indices for mode transition gait cycles and calculate transition rmse
# l_transition_cycles, r_transition_cycles = find_mode_transition_cycles(l_data, r_data)
# transitions = np.unique(list(l_transition_cycles.keys()))
# transition_rmse = {}
# for transition in transitions:   
#     l_transition_data = r_transition_data = pd.DataFrame([])
#     for indeces in l_transition_cycles[transition]:
#         l_transition_data = l_transition_data.append(l_data.iloc[indeces[0]:indeces[1]+1, :])
#     for indeces in r_transition_cycles[transition]:
#         r_transition_data = r_transition_data.append(r_data.iloc[indeces[0]:indeces[1]+1, :])   
#     l_rmse = custom_rmse(l_transition_data.iloc[:, -8:-4].to_numpy(), 
#                                     l_transition_data.iloc[:, -4:].to_numpy())
#     r_rmse = custom_rmse(r_transition_data.iloc[:, -8:-4].to_numpy(), 
#                                     r_transition_data.iloc[:, -4:].to_numpy())
#     transition_rmse[transition] = np.mean((l_rmse[0], r_rmse[1]))
# # Calculate mode specific rmse
# l_ntransition_data = l_data.drop(index=l_transition_data.index)
# l_modes = l_ntransition_data['leftWalkMode'].unique()
l_modes = l_data['leftWalkMode'].unique()
l_mode_rmse = {}
for mode in sorted(l_modes):
    # mode_data = l_ntransition_data[l_ntransition_data['leftWalkMode'] == mode]
    mode_data = l_data[l_data['leftWalkMode'] == mode]
    l_mode_rmse[f'mode {mode}'] = custom_rmse(mode_data.iloc[:, -8:-4].to_numpy(), 
                                  mode_data.iloc[:, -4:].to_numpy())

# r_ntransition_data = r_data.drop(index=r_transition_data.index)
# r_modes = r_ntransition_data['rightWalkMode'].unique()
r_modes = r_data['rightWalkMode'].unique()
r_mode_rmse = {}
for mode in sorted(r_modes):
    # mode_data = r_ntransition_data[r_ntransition_data['rightWalkMode'] == mode]
    mode_data = r_data[r_data['rightWalkMode'] == mode]
    r_mode_rmse[f'mode {mode}'] = custom_rmse(mode_data.iloc[:, -8:-4].to_numpy(), 
                                  mode_data.iloc[:, -4:].to_numpy())
mode_rmse = {}
for mode in sorted(r_modes):
        mode_rmse[f'mode {mode}'] = np.mean((l_mode_rmse[f'mode {mode}'][0], r_mode_rmse[f'mode {mode}'][1]))

# segments = data['mag'].unique()
# segments = segments[segments != -1]

# segment_rmse = {}
# for segment in sorted(segments):
#     l_segment_data = l_data[l_data['mag'] == segment]
#     r_segment_data = r_data[r_data['mag'] == segment]
#     l_rmse = custom_rmse(l_segment_data.iloc[:, -9:-5].to_numpy(), 
#                          l_segment_data.iloc[:, -4:].to_numpy())
#     r_rmse = custom_rmse(r_segment_data.iloc[:, -9:-5].to_numpy(), 
#                          r_segment_data.iloc[:, -4:].to_numpy())
#     segment_rmse[segment] = (l_rmse[0] + r_rmse[1])/2

# print(filename)
# print('segment rmse: ', segment_rmse)
# segment_rmse = pd.DataFrame(segment_rmse, index=[0])

# print('mode transition gait cycle rmse: ', '{:.2f}'.format(np.mean(list(transition_rmse.values()))))
# print('transition rmse breakdown: ', transition_rmse)
print('mode rmse: ', mode_rmse)

# pd.options.display.float_format = '{:.2f}'.format
# segment_rmse.to_excel('segment_rmse.xlsx')
# column_list = ['subject', 'method', 'overall', 'transition', 'sd-lg', 'sa-lg', 
#                'rd-lg', 'ra-lg', 'lg-ra', 'lg-rd', 'lg-sa', 'lg-sd', 'lg', 
#                'ra', 'rd', 'sa', 'sd']

# results = [subject, method, np.mean(overall_rmse), np.mean(list(transition_rmse.values()))] + list(transition_rmse.values()) + list(mode_rmse.values())
# results = pd.DataFrame(results).transpose()
# results.columns = column_list
# print(results)
# output = pd.read_excel('output.xlsx', index_col=0)
# output = output.loc[~((output['subject']==subject) & (output['method']==method))]
# output = output.append(results)
# output = output.sort_values(['subject', 'method'])

# print('\n\nRESULTS:\n')
# print(output.to_string(index=False))
# print('\n\n')
# output.to_excel('output.xlsx')