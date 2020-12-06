FILES_STATUS="Not"

if [[ $CHANGED_FILES =~ (docker\/dvc-for-cd4ml\.Dockerfile|dvc-for-cd4ml-conda\.yaml) ]] ;
then FILES_STATUS="Matched";
fi

echo $FILES_STATUS
