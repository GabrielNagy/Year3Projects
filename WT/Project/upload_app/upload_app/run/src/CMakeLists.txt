include_directories (${TEMPLATE_SOURCE_DIR}/src)
include_directories (${TEMPLATE_SOURCE_DIR}/gmock-1.7.0/include)
include_directories (${TEMPLATE_SOURCE_DIR}/gmock-1.7.0/gtest/include)


add_library (template templateSrc.cc) 


add_executable (templateTest templateTest.cc)
target_link_libraries (templateTest template gmock_main)  

add_test (templateTest templateTest)
