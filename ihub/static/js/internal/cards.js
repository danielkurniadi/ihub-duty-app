
// main function

function handleTaskCardsDisplay(cardSelectors){
    // inner func
    function _collapseToggle(card$Obj){
        card$Obj.forEach(obj =>{
            const [card$, collapseBtn$] = obj;
            collapseBtn$.click(function(){
                card$.collapse('toggle');
                return false;
            })
        });
        return; 
    };

    // inner func
    function _swapOnSubmit({active, completed, submitBtn$}){
        submitBtn$.click(function(){
            $(completed).show();
            $(active).remove();
            return false;
        });
    }

    cardSelectors.forEach(cardPair => {
        const {active, completed} = cardPair;
        
        // active
        activeBody$ = $(active).find(".card");
        activeCollapseBtn$ = $(active).find(".collapseBtn");
        submitBtn$ = $(active).find(".submitTaskBtn");

        // completed
        completedBody$ = $(completed).find(".card");
        completedCollapseBtn$ = $(completed).find(".collapseBtn");

        // handle Collapse Toggle
        _collapseToggle([
            [activeBody$, activeCollapseBtn$],
            [completedBody$, completedCollapseBtn$],
        ])
        _swapOnSubmit({active, completed, submitBtn$})
    });

    return
}