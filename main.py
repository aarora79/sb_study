# -*- coding: utf-8 -*-
def main(argv):
    num_args = len(argv)
    print(num_args)
    if num_args < NUM_ARGS_NEEDED:
        print('did not find sufficient number of arguments, needed ' + str(NUM_ARGS_NEEDED) + ', got ' + str(num_args))
        print('Usage: python aqi.py <zip code list filename>')
        sys.exit(1)
    #input params look ok.
    file_name = argv[1]  
    
    #call the function that does the work
    get_and_save_aqi_data(file_name)
                    
if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)

