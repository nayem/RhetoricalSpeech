function NLP_createNoisySpeech(CLASS,NUMS_OF_CUTS, NOISE,TASK, SNR)

% createNoisySpeech_v2() Summary of this function goes here
%
%   Create noisy wav files
%
%   Nayem, Apr 7, 2018

    % Train-> -3dB, 0dB, +3dB
    % Dev-> -3dB, 0dB, +3dB
    % Test-> -6dB, -3dB, 0dB, +3dB, +6dB

    %SNR = 6;

%     NUMS_OF_CUTS = 1;

    % TASK = 'TRAIN';
    % TASK = 'DEV';
    % TASK = 'TEST';
    
    if strcmpi(TASK, 'TRAIN')
        
        if strcmpi(CLASS, 'Question')
            % Create Noisy Training
            Clean_Wav_Save_Path = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Question_16k/train_16k';
            Noisy_Wav_Save_Path = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Question_16k/NLP_train_16k';
        else
            % Create Noisy Training
            Clean_Wav_Save_Path = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Declarative_16k/train_16k';
            Noisy_Wav_Save_Path = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Declarative_16k/NLP_train_16k';
        end

    elseif strcmpi(TASK, 'VAL')
        if strcmpi(CLASS, 'Question')
            % Create Noisy Development
            Clean_Wav_Save_Path = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Question_16k/val_16k';
            Noisy_Wav_Save_Path = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Question_16k/NLP_val_16k';
        else
            % Create Noisy Training
            Clean_Wav_Save_Path = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Declarative_16k/val_16k';
            Noisy_Wav_Save_Path = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Declarative_16k/NLP_val_16k';
        end
        
    elseif strcmpi(TASK, 'TEST')
        if strcmpi(CLASS, 'Question')
            % Create Noisy Testing
            Clean_Wav_Save_Path = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Question_16k/test_16k';
            Noisy_Wav_Save_Path = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Question_16k/NLP_test_16k';
        else
            % Create Noisy Training
            Clean_Wav_Save_Path = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Declarative_16k/test_16k';
            Noisy_Wav_Save_Path = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Declarative_16k/NLP_test_16k';
        end
        
    end


    Noise_Wav_Path = '/Users/nayem/Downloads/IU/Spring 2018/Noises10_16k';


    file_list = dir( fullfile(Clean_Wav_Save_Path,'*.wav'));


    if strcmpi(NOISE, 'Babble')
        Noise_file_name = 'babble_16k.wav';

    elseif strcmpi(NOISE, 'Cafe')
        Noise_file_name = 'cafe_16k.wav';

    elseif strcmpi(NOISE, 'Car')
        Noise_file_name = 'car_16k.wav';

    elseif strcmpi(NOISE, 'Factory')
        Noise_file_name = 'factory_16k.wav';
        
    elseif strcmpi(NOISE, 'MachineGun')
        Noise_file_name = 'machinegun_16k.wav';

    elseif strcmpi(NOISE, 'Plane')
        Noise_file_name = 'plane_16k.wav';

    elseif strcmpi(NOISE, 'Restaurant')
        Noise_file_name = 'restaurant_16k.wav';

    elseif strcmpi(NOISE, 'SSN')
        Noise_file_name = 'ssn_16k.wav';
        
    elseif strcmpi(NOISE, 'Tank')
        Noise_file_name = 'tank_16k.wav';

    elseif strcmpi(NOISE, 'White_Noise')
        Noise_file_name = 'white_noise_16k.wav';
    end


    %%
    [Masker, F_masker] = audioread(fullfile(Noise_Wav_Path,Noise_file_name) );

    for n = 1:length(file_list)
        target_path = fullfile(file_list(n).folder,file_list(n).name );
        [Target, F_target] = audioread(target_path);

        fprintf('target:%s\n', target_path);
        
        %% Original audio file read write
        fname = (strsplit(file_list(n).name,'.'));
        noisy_file_name = sprintf('%s_%02d.%s',fname{1}, 0, fname{2});
        noisy_file_path = fullfile(Noisy_Wav_Save_Path,noisy_file_name);
        audiowrite(noisy_file_path, Target, F_target);
            
        mixture_target_masker = generateMixture_v2(double(Target),double(Masker),SNR , TASK,NUMS_OF_CUTS);

        mtm_size = size(mixture_target_masker);
        
        if length(mtm_size) < 3
            num_cut = 1;
        else
            num_cut = mtm_size(3);
        end

        for k = [1:num_cut]
            %% Audio file read write
            mixture = mixture_target_masker(:,1,k);
            target = mixture_target_masker(:,2,k);
            masker = mixture_target_masker(:,3,k);

            noisy_file_name = sprintf('%s_%s_%02d_%+ddB.%s',fname{1}, NOISE, k, SNR,fname{2});
            noisy_file_path = fullfile(Noisy_Wav_Save_Path,noisy_file_name);
            audiowrite(noisy_file_path, mixture./max(abs(mixture)), F_target);
        end




    end
end