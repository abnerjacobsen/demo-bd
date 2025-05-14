# -----------------------------------------------------#
#                       Project rename                 #
# -----------------------------------------------------#
# """ Rename the project name, imports, docs, etc.

#     Credits:
#     Abner G Jacobsen
#     https://github.com/abnerjacobsen
# """
find . -type f -exec sed -i 's/demo-bd/change-me/g' {} +
find . -type f -exec sed -i 's/demo_bd/change_me/g' {} +

find . -type d -name 'demo_bd' | while read FILE ; do
    newfile="$(echo ${FILE} |sed -e 's/demo_bd/change_me/')" ;
    mv "${FILE}" "${newfile}" ;
done

find . -type d -name 'demo-bd' | while read FILE ; do
    newfile="$(echo ${FILE} |sed -e 's/demo-bd/change-me/')" ;
    mv "${FILE}" "${newfile}" ;
done

rm -f .git/index
git reset

