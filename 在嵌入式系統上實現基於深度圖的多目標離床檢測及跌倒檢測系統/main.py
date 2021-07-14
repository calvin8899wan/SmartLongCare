if __name__ == '__main__':
    # Initialize the library with the path containing the module
    pyK4A = pyKinectAzure(modulePath)

    # Open device
    pyK4A.device_open()

    # Modify camera configuration
    device_config = pyK4A.config
    device_config.color_resolution = _k4a.K4A_COLOR_RESOLUTION_1536P
    print(device_config)

    # Start cameras using modified configuration
    pyK4A.device_start_cameras(device_config)

    # k = 0
    for i in range(20):
        # Get capture
        pyK4A.device_get_capture()

        # Get the color image from the capture
        color_image_handle = pyK4A.capture_get_color_image()

        # Check the image has been read correctly
        if color_image_handle:
            # Read and convert the image data to numpy array:
            color_image = pyK4A.image_convert_to_numpy(color_image_handle)

            # Plot the image
            # cv2.namedWindow('Color Image',cv2.WINDOW_NORMAL)
            # cv2.imshow("Color Image",color_image)
            outputImage3 = color_image
            
            outputImage3=outputImage3[316:1694,137:1399]
            outputImage3=cv2.resize(outputImage3,(640,576))
            cv2.imwrite('outputImage3.jpg', outputImage3)
            print("okay")
            # k = cv2.waitKey(1)

            # Release the image
            pyK4A.image_release(color_image_handle)

        pyK4A.capture_release()

    # if k==27:    # Esc key to stop
    # break
    
    pyK4A.device_stop_cameras()
    pyK4A.device_close()
 

   



    ###################
    pyK4A = pyKinectAzure(modulePath)
    pyK4A.device_open()

    device_config = pyK4A.config
    device_config.color_resolution = _k4a.K4A_COLOR_RESOLUTION_1080P
    device_config.depth_mode = _k4a.K4A_DEPTH_MODE_NFOV_UNBINNED
    print(device_config)

    pyK4A.device_start_cameras(device_config)
    pyK4A.bodyTracker_start(bodyTrackingModulePath)

    # 讀xyxy
    elements = []
    with open(labelpath) as file:
        for line in file:
            line = line.strip().split()
            elements.append(line)
    ele_array = np.array(elements)
    # print('%s\nshape is %s' % (type(ele_array), ele_array.shape))

    file.close()

    min_x = int(ele_array[0, 1])-80
    min_y = int(ele_array[0, 2])+80
    max_x = int(ele_array[0, 3])-135
    max_y = int(ele_array[0, 4])+20
    show = [min_x,min_y,max_x,max_y]

    # 讀xyxy
    # alarm img
    alarm_image = cv2.imread('alarm_image.jpg')
    safe_image = cv2.imread('safe_image.jpg')
    alarm_image=cv2.resize(alarm_image, (300, 300))
    safe_image=cv2.resize(safe_image, (300, 300))
    bed = 0

    k = 0
    while True:
        pyK4A.device_get_capture()
        depth_image_handle = pyK4A.capture_get_depth_image()

        if depth_image_handle:

            pyK4A.bodyTracker_update()
            depth_image = pyK4A.image_convert_to_numpy(depth_image_handle)
            depth_color_image = cv2.convertScaleAbs(depth_image, alpha=0.05)
            depth_color_image = cv2.cvtColor(depth_color_image, cv2.COLOR_GRAY2RGB)

            for body in pyK4A.body_tracker.bodiesNow:
                skeleton2D = pyK4A.bodyTracker_project_skeleton(body.skeleton)
                # pyK4A.body_tracker.printBodyPosition(body)#print position
                # print(skeleton2D.joints2D[_k4abt.K4ABT_JOINT_HANDTIP_RIGHT].position.v[0])
                # print(skeleton2D.joints2D[_k4abt.K4ABT_JOINT_HANDTIP_RIGHT].position.v[1])
                # print(f"BodyId: {body.id}", \
                # f"X: {int(skeleton2D.joints2D[_k4abt.K4ABT_JOINT_HANDTIP_RIGHT].position.v[0])} ", \
                # f"Y: {int(skeleton2D.joints2D[_k4abt.K4ABT_JOINT_HANDTIP_RIGHT].position.v[1])} ") 
                X_pos = int(skeleton2D.joints2D[_k4abt.K4ABT_JOINT_SPINE_NAVEL].position.v[0])
                Y_pos = int(skeleton2D.joints2D[_k4abt.K4ABT_JOINT_SPINE_NAVEL].position.v[1])
                print(f"BodyId: {body.id}", f"skeleton_position:{X_pos, Y_pos}")

                num_bodies = pyK4A.body_tracker.get_num_bodies()

                for i in range(num_bodies):
                    # if body.id  == num_bodies:

                    if X_pos > min_x and X_pos < max_x:
                        if Y_pos > min_y and Y_pos < max_y:
                            #cv2.putText(safe_image, str(body.id), (40, 50), cv2.FONT_HERSHEY_PLAIN, 2.0,
                                        #(0, 0, 255), 2)
                            #cv2.imshow('alarm_image1' + str(body.id), safe_image)
                            show_state=0
                            #cv2.destroyWindow('alarm_image1' + str(body.id))
                            #safe_image = cv2.imread('safe_image.jpg')
                            #safe_image=cv2.resize(safe_image, (300, 300))

                            print("on bed")

                        else:
                            #cv2.putText(alarm_image, str(body.id), (40, 50), cv2.FONT_HERSHEY_PLAIN, 2.0,
                                       # (0, 0, 255), 2)
                            #cv2.imshow('alarm_image1' + str(body.id), alarm_image)
                            show_state=1
                            #cv2.destroyWindow('safe_image1' + str(body.id))
                            #alarm_image = cv2.imread('alarm_image.jpg')
                            #alarm_image=cv2.resize(alarm_image, (300, 300))
                            print("fall detection begin!!!")
                    else:
                        #cv2.putText(alarm_image, str(body.id), (40, 50), cv2.FONT_HERSHEY_PLAIN, 2.0, (0, 0, 255),
                                    #2)
                        #cv2.imshow('alarm_image1' + str(body.id), alarm_image)
                        show_state=1
                        #cv2.destroyWindow('safe_image1' + str(body.id))
                        #alarm_image = cv2.imread('alarm_image.jpg')
                        #alarm_image=cv2.resize(alarm_image, (300, 300))
                        print("fall detection begin!!!")

                combined_image = pyK4A.body_tracker.draw2DSkeleton(skeleton2D, body.id, depth_color_image)
                

                ######################################## FALL {
                                # LOOT 25 FROM 32 POINTS
                print('=================================================')
                print('A : BODY ID CHECK     ',body.id)
                print('=================================================')
                #print('len of LIST',len(YJ_input_list)-1)



                xyz_75 = skeleton_by_look_up_table(body) #(1, 75)
                #CHECK ID EXIST BEFORE : IF NOT EXIT : CREATE A Skeletons list
                # SETUP STACK skeletons TO 30 FRAMES      
                
                print('B LABEL EXIST',label_exist)
                if label_exist< body.id:
                    #for i in body.id:
                    write_times = body.id - label_exist  # 9
                    for i in range(write_times):
                        if i==write_times-1:
                            label_exist = body.id
                            YJ_input_list.append(xyz_75)
                            state.append(0)
                            print('B-2 LABEL CHANGE',label_exist)
                        else:
                            YJ_input_list.append(0)
                            state.append(0)
                else:
                    YJ_input_list[body.id] = np.append(YJ_input_list[body.id],xyz_75,axis=0) #(1, 75)
                
                if YJ_input_list[body.id].shape[0]==31: #the first time have 25 frames will be at frame 24
                    #print('YJ_input',YJ_input.shape)
                    YJ_input_list[body.id] = np.delete(YJ_input_list[body.id],obj=0,axis =0)
                else:
                    print('BODY ID:',body.id, 'is filling')
                    print('filled shpae',YJ_input_list[body.id].shape)
                    continue
                
                
                print('C model input shape',YJ_input_list[body.id].shape,', ID is',body.id)   #C (30, 75)

                # THE (1,30,75) TO MODEL INFERENCE
                YJ_input_model = np.reshape(YJ_input_list[body.id],(1,30,75))
                
                acc = sess.run(fc,feed_dict={skeleton:YJ_input_model,training:False})
                #label = tf.placeholder(tf.float32, shape=[1, 2])   
                
                if (show_state ==0):
                    print(body.id,'on bed')
                    cv2.imshow('alarm_{}'.format(body.id),safe_image)
                
                elif  (acc[0][0] > acc[0][1])and show_state==1:
                    print(body.id,'SAVE')
                    state[body.id-1]= 0
                    #cv2.putText(safe_image, 'index '+str(body.id), (40, 30), cv2.FONT_HERSHEY_TRIPLEX, 1.0,(255, 0, 0), 2)
                    cv2.imshow('alarm_{}'.format(body.id),alarm_image)
                else:
                    print(body.id,'DANGER')
                    #cv2.putText(alarm_image,'index '+str(body.id), (40, 30), cv2.FONT_HERSHEY_TRIPLEX, 1.0,(255, 0, 0), 2)
                    cv2.imshow('alarm_{}'.format(body.id),fall_alarm)
                    state[body.id-1]= 1
                ####}

                    
            plot_one_box(show, depth_color_image)
            cv2.imshow('Segmented Depth Image', depth_color_image)
            k = cv2.waitKey(1)

            # Release the image
            pyK4A.image_release(depth_image_handle)
            pyK4A.image_release(pyK4A.body_tracker.segmented_body_img)

        pyK4A.capture_release()
        pyK4A.body_tracker.release_frame()

        if k == 27:  # Esc key to stop
            break


    pyK4A.device_stop_cameras()
    pyK4A.device_close()
