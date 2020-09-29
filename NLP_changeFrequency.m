function NLP_changeFrequency( CLASS)
% CHANGEFREQUENCY Summary of this function goes here
%
%   Change the frequency of the .wav
%   Use it to convert into 16kHz wav files
%
%   Nayem, May 01, 2018


    DesiredFrequency = 16e3;
    suffix = '16k';
       
    if strcmpi(CLASS, 'Question')
        inputPath = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Question';
        outputPath_train = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Question_16k/train_16k';
        outputPath_val = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Question_16k/val_16k';
        outputPath_test = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Question_16k/test_16k';
    else
        inputPath = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Declarative';
        outputPath_train = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Declarative_16k/train_16k';
        outputPath_val = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Declarative_16k/val_16k';
        outputPath_test = '/Users/nayem/Downloads/IU/Spring 2018/CSCI-B 659 NLP/Declarative_16k/test_16k';
    end

    wav_file_suffix = '*.wav';
    
    train_prob = 0.75;
    test_prob = 0.2 + train_prob;

    inputFiles     = dir(fullfile(inputPath, wav_file_suffix ));

    for i=1:length(inputFiles)

        if rand <= train_prob
            outputPath = outputPath_train ;
        elseif rand <= test_prob
            outputPath = outputPath_test ;
        else
            outputPath = outputPath_val ;
        end

        %% Audio file read write
        [Y,Fs] = audioread(fullfile(inputFiles(i).folder,inputFiles(i).name));

        Ynew = resample(Y,DesiredFrequency,Fs);

        fname = (strsplit(inputFiles(i).name,'.'));
        output_filename = sprintf('%s_%s.%s', fname{1},suffix,fname{2});
        output_path = fullfile(outputPath,output_filename);
        disp(output_path);
        audiowrite(output_path, Ynew, DesiredFrequency);


    end

end

