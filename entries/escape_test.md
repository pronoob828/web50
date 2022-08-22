# heading
creating a list with \\ before asterisk

\* shouldn't 
\* be a  
\* list

list without a blank line before-  
* shouldn't be 
* a list

\*\* shouldn't be bold\*\*  
\*shouldn't be italic\*


\# shouldn't be heading
# heading 

list with styled text

* **should be bold**
* *italic here* 

Multiple lists became a problem because It would consider everything after the beginning of the list to be a ul, since the regex pattern had to be greedy, had to make big changes to the way lists are detected... you are probably not interested in this, but I need something to write as a test paragraph , because apparently the horizontal break at the bottom can behave rather strange sometimes