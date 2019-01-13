var wikibaseRootUrl = 'https://www.wikidata.org/wiki/';
var wikibaseApiUrl = 'https://www.wikidata.org/w/api.php';
var lang = 'en';
var entityIdRegex = /^([A-Z][a-z]*:)?[QPL][1-9]\d*/;


/**
 * Given a list of entity ids (max 50 values), query the API
 * to render them in HTML
 *
 * entityIds: list of entity ids to render
 * elements: map from entity ids to lists of elements to replace by
 *      the rendered values
 */
function renderEntities(entityIds, elements) {
   var renderCallback = function(data) {
       if (data.success !== 1) {
           return;
       }
       var renderedEntities = data.wbformatentities
       for(var id in renderedEntities) {
          if(!renderedEntities.hasOwnProperty(id)) {
              continue;
          }
          var rendered = renderedEntities[id];
          for(let elem of elements.get(id).values()) {
             elem.replaceWith(rendered);  
          }
       }
   };
   $.ajax({
     url: wikibaseApiUrl,
     dataType: 'jsonp',
     data: {
         'ids': entityIds.join('|'),
         'action': 'wbformatentities',
         'format': 'json',
         'uselang': lang},
     success: renderCallback
  });
}

/**
 * Renders all Wikibase entities linked to in the DOM.
 */
function renderEntitiesInDOM() {
    // Gather the mentions of all entities
    var elements = new Map();
    $('a').each(
        function(idx) {
           var elem = $(this);
           var href = elem.attr('href');
           var text = elem.text();
           if (wikibaseRootUrl + text === href && entityIdRegex.test(text)) {
                // Remove namespace, as it is not expected by wbformatentities
                if(text.indexOf(':') !== -1) {
                    text = text.split(':')[1];
                }
                
                // Index element by entity id
                var otherElems = elements.get(text);
                if(otherElems === undefined) {
                    otherElems = [];
                    elements.set(text, otherElems);
                }
                otherElems.push(elem);
           }
    });

    // Render all the entities
    var idsSeen = Array.from(elements.keys());
    var batch = idsSeen.splice(0,50);
    while (batch.length > 0) {
        renderEntities(batch, elements);
        batch = idsSeen.splice(0,50);
    }
}

$(function() {
    renderEntitiesInDOM();
});
