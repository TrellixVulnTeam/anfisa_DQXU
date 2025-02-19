ds_stat
=======
        **Filtering regime support**
        
.. index:: 
    ds_stat; request

Synopsis
--------
**ds_stat** 

    **Arguments**: 

        **ds**: dataset name
        
        **tm**: *optional* time delay control option, in seconds, *float*

        **filter**: *optional* name of applying filter
        
        **conditions**: *optional* list of applying :doc:`condition descriptors<s_condition>`
            *in JSON string representation*

        **ctx**: *optional*, :doc:`context descriptor<s_stat_ctx>`
            *in JSON string representation*
            
        **actsym**: *optional*, add gene symbols from filter to :ref:`active symbols<actsym_purpose>` 
            *recommended in form* ``actsym=1``
        
        **instr**: *optional modifier* 
        
    |       ``[``
    |           **[0]**: option, ``"UPDATE"``, ``"DELETE"`` *or* ``"JOIN"``
    |           **[1]**: filter name, *string*
    |           **[2]**: rubric, in case of ``"UPDATE"`` option,  *optional string*
    |               *position [2] is optional and can be omited*
    |       ``]`` *in JSON string representation*
        
    **Return value**: 
    
    | ``{`` *dictionary*
    |      "**kind**": kind of dataset, ``"ws"`` *or* ``"xl"``
    |      "**total-counts**": count of items in dataset
    |           ``[`` *list**
    |               **[0]** count of DNA variants, *int*
    |               **[1]** *optional* count of transcript variants, *int*
    |               **[2]** *optional* count of transcripts, *int*
    |           ``]``
    |      "**filtered-counts**": count of items filtered
    |           ``[`` *list**
    |               **[0]** count of variants, *int*
    |               **[1]** *optional* count of transcript variants, *int*
    |               **[2]** *optional* count of transcripts, *int*
    |           ``]``
    |      "**stat-list**": ``[`` *list of* :doc:`s_prop_stat` ``]``
    |      "**functions**": ``[`` *list of* :doc:`s_prop_stat` for functions ``]``
    |      "**cur-filter**: *optional* name of current filter, *string*
    |      "**conditions**:  ``[`` *list of* :doc:`s_condition` ``]``
    |      "**cond-seq**: render information for conditions
    |           ``[`` *list* 
    |               ``{`` *dictionary* 
    |                    "**repr**": condition HTML-representation, *string*
    |                    "**err**: *optional* error status, *string*
    |                    "**unit**": *optional* name of base condition property, *string*
    |               ``}``, ...
    |           ``]``
    |      "**eval-status**": status of current conditions evaluation
    |              ``"ok"`` if evaluation is correct, other *string* otherwise
    |      **hash**: hash code associated with current filter conditions, *string*
    |      **filter-list**: names of all filters available for dataset
    |           ``[`` *list of* :doc:`s_sol_entry` ``]``
    |      **filter-sol-version**: :ref:`indicator of state<sol_version_indicators>` for filters
    |      **rq_id**": unique request id, for use in secondary requests, *string*
    |  ``}``
    
Description
-----------
The request is the principal one for organizing :term:`filtering regime<filter>` for :term:`datasets<dataset>`. 

The most important functionality initiated by this method is :doc:`../concepts/status_report`, see there explanations of input argument **tm** and returning properties **stat-list**, **functions**, **rq-id**

The rest of information returning by the request concerns filters as :doc:`../concepts/sol_work`.

Current conditions/filter define :term:`filter` if either **filter** or **conditions** is set (see discussion :ref:`here<fiter_conditions>`). 
Otherwise (and also if **conditions** is set as empty list) the full dataset is subject of request.

Returning property **cur-filter** is not null if current conditions are stored on the server side as filter with correspondent filter name. (Property **hash** contains hash of current conditions)

Returning property **conditions** contains conditions in operational format(:doc:`s_condition`). But for rendering needs the request returns additionally the list **cond-seq** and status **eval-status**. In most common scenario conditions are correct and can be evaluated property, however there might be errors, and information about these errors should be used by the client. Please pay attention at property **unit** in **cond-seq** list: usually it is equal to  value of second element ([1]) of correspondent condition from **conditions**. But existence of **unit** property guarantees that condition has no errors.

Returning properties **total-counts** and **filter-counts** have length of 3 in case of :term:`workspaces<workspace>` and length of 1 otherwise. Second position in lists correspond to counts of :term:`transcript variants<transcript variant>` and :term:`transcripts<transcript>`.

Modification of filters
^^^^^^^^^^^^^^^^^^^^^^^
If argument **instr** is set, the request modifies filter on server side in the following cases:

   * ``["UPDATE", <filter_name>, <rubric>]`` the value of argument **conditions** are interpreted as new content of filter ``filter_name``, use this option for both create or update filter
    
   * ``["UPDATE", <filter_name>]`` the same as previous, with no rubric change
    
   * ``["DELETE", <filter_name>]`` the filter ``filter_name`` is subject to be deleted.
     
In case ``["JOIN", <filter_name>]`` the request modifies current condiitons collected from **conditions** or **filter** by joining them with content of named filter ``filter_name``.
     
See also :doc:`../concepts/sol_work`

Comments
--------
The request has simple analogue :doc:`dtree_stat`: both methods initiate :doc:`../concepts/status_report`.

Also the request has analogue :doc:`dtree_set`: both methods support its main objects as :doc:`../concepts/sol_work`, this request does it for :term:`filters<filter>`, decision tree request for :term:`decision trees<decision tree>`.

See also
--------
:doc:`statunits`     

:doc:`statfunc`

:doc:`../concepts/status_report`  

:doc:`../concepts/sol_work`

