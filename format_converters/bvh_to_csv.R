library("RMoCap")
library("docstring")
library("optparse")
library("dplyr")

bvh_to_direct_kinematic_csv <- function(bvh_file_path, csv_file_path, no_rotation = F){
  #' Reads in a bvh file and converts to a direct kinematic representation. This is then saved to a csv
  #' @param bvh_file_path The path to the bvh file to be converted to kinematic representation
  #' @param csv_file_path The path where the resulting csv will be saved
  print(bvh_file_path)
  #bvh_file_path <- "D:/TCDFiles/3dGeom/SquatData/SquatMeshes/bvh_no_space/Business_Female_01#air_squat.bvh"
  #csv_file_path <- "D:/TCDFiles/3dGeom/SquatData/SquatMeshes/csv_world_pos/Business_Female_01#air_squat.csv"
    
  if(!file.exists(bvh_file_path)){
    stop(paste("Please provide a valid file path, ", bvh_file_path, "doesn't exist"))
  }
  else{
    bvh_data <- read.mocap(bvh_file_path)
    print(paste("Writing mocap to ", csv_file_path))
    print(summary(bvh_data))
    forward_kinematic <- hierarchical.to.direct.kinematic(bvh_data$skeleton)
    
    if(no_rotation){
      forward_kinematic <- forward_kinematic[, grepl(".D|Time", names(forward_kinematic))]
    }
    write.csv(forward_kinematic, file = csv_file_path)
  }
}

main <- function(){
  option_list <- list(
    make_option(c( "--bvh_file_path","-i"), type = "character", default = NULL,
                help = "The path to the bvh file to be converted to kinematic representation"),
    
    make_option(c("--csv_file_path", "-o"), type = "character", default = NULL,
                help = "The path where the resulting csv will be saved")
  )
  opt_parser <- OptionParser(option_list = option_list)
  opt = parse_args(opt_parser)
  print(paste("read args: ", opt))
  bvh_to_direct_kinematic_csv(opt$bvh_file_path, opt$csv_file_path)
}
#security_male <- read.mocap("D:/TCDFiles/3dGeom/SquatData/SquatMeshes/test.bvh")
#plot.mocap(security_male, alpha = 0.5, spheres = TRUE, print.text = FALSE, frame = 1)
#df <- hierarchical.to.direct.kinematic(security_male$skeleton)
#write.csv(df, file = "D:/TCDFiles/3dGeom/SquatData/SquatMeshes/test.csv")
#summary.mocap(security_male)

main()

