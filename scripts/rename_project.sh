# -----------------------------------------------------#
#                       Project rename                 #
# -----------------------------------------------------#
# """ Rename the project name, imports, docs, etc.

#     Credits:
#     Abner G Jacobsen
#     https://github.com/abnerjacobsen
# """
find . -type f -exec sed -i 's/snap-backend-template/change-me/g' {} +
find . -type f -exec sed -i 's/snap_backend_template/change_me/g' {} +

find . -type d -name 'snap_backend_template' | while read FILE ; do
    newfile="$(echo ${FILE} |sed -e 's/snap_backend_template/change_me/')" ;
    mv "${FILE}" "${newfile}" ;
done

find . -type d -name 'snap-backend-template' | while read FILE ; do
    newfile="$(echo ${FILE} |sed -e 's/snap-backend-template/change-me/')" ;
    mv "${FILE}" "${newfile}" ;
done

rm -f .git/index
git reset

