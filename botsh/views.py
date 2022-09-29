import json
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse

import os
import rdflib
from rdflib import Graph, Namespace
# Create your views here.


inputfile = r"botsh-duplex.ttl"
boshinputfile = r"BOSH-SmartHomeBuildingOntology.ttl"

#production file path
#inputfile = r"/home/botsh/botsh_demo/botsh-duplex.ttl"
#boshinputfile = r"/home/botsh/botsh_demo/BOSH-SmartHomeBuildingOntology.ttl"

def index(request):
    return render(request,'index.html')


def runquery(request):

    question = request.POST['questionsbox']
    print(question)
    query1 = """
    PREFIX botsh: <http://purl.org/botsh#>
    PREFIX inst: <http://purl.org/botsh/p1#>
select * where { 
	?storey a botsh:BuildingStorey.
    ?storey botsh:hasSpace ?space.
} limit 100
    """
    query2 = """
        PREFIX botsh: <http://purl.org/botsh#>
    select ?storey ?space ?element ?subelement where { 
	?storey a botsh:BuildingStorey. ?storey botsh:hasSpace ?space.
    optional {?space botsh:hasElement ?element.}
    optional {?element botsh:hasSubElement ?subelement.}} 
limit 100
        """
    query3 = """
            PREFIX botsh: <http://purl.org/botsh#>
        select ?space ?adjelement ?intelement where { ?space a botsh:Space.
   optional {?space botsh:adjacentElement ?adjelement.}    
   optional {?space botsh:intersectingElement  ?intelement.}}
    limit 100
            """
    query4 = """
            PREFIX botsh: <http://purl.org/botsh#>
            PREFIX bosh: <http://purl.org/bosh#>
        select distinct ?thing where {?thing a botsh:Thing. ?thing a bosh:SensingDevice.}
    limit 100
            """
    query5 = """
            PREFIX botsh: <http://purl.org/botsh#>
            PREFIX bosh: <http://purl.org/bosh#>
        select ?storey ?space ?element ?thing ?value ?unit where { 
    ?storey a botsh:BuildingStorey. ?storey botsh:hasSpace ?space. 
?space botsh:adjacentElement ?element. ?element botsh:containsThing ?thing. 
?thing a bosh:TemperatureSensor. ?thing bosh:measuresQuantity ?q. ?q bosh:hasValue ?value. ?q bosh:hasUnitOfMeasure ?u. ?u bosh:hasUnitValue ?unit. filter(?storey=<http://purl.org/botsh/p1#level_1xS3BCk291UvhgP2dvNMKI>)} 
    limit 100
            """

    queryselection = {'1':query1, '2':query2,'3':query3, '4':query4, '5':query5}
    cq = {'1': 'CQ1 - What are the different spaces present in the building?',
             '2': 'CQ2 - What are the tangible building elements and sub elements present in the building?',
             '3': 'CQ3 - What are the adjacent and intersecting elements within the building?',
             '4': 'CQ4 - What are all the different types of sensors present within the building?',
             '5': 'CQ5 - What are the room temperatures pertaining to a particular storey of the building?'
             }
    g = rdflib.Graph()
    g.parse(inputfile, format=rdflib.util.guess_format(inputfile))
    g.parse(boshinputfile,format=rdflib.util.guess_format(boshinputfile))
    results = g.query(queryselection[question])
    print(results)
    # for storey, space in results:
    #     print(storey,space)
    pd.DataFrame(results.bindings)

    # converts everything to strings including missing values
    pd.DataFrame(results.bindings).applymap(str).rename(columns=str)

    # serialize with json and then parse (clobbers types, converting values to strings)

    results_json = results.serialize(format="json")
    bindings = json.loads(results_json)["results"]["bindings"]
    bindings = [{k: v["value"] for k, v in result.items()} for result in bindings]
    df = pd.DataFrame(bindings)
    context = {
        'df_dict': df.to_dict(),
        'df_rec': df.to_dict(orient='records'),
        'query': queryselection[question],
        'question': cq[question]
    }
    return render(request,'index.html', context)
