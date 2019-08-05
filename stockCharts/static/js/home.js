var stock_id, stock_name, stock_code
//$(document).ready(function() {
//	
////    $("#serachForm").on("submit", function() {
////    	
//////    	var stock_id = $("#stock-input-auto").val();
////    	var img_url = "https://fn-chart.dunamu.com/images/kr/candle/d/" + stock_id + ".png";
////    	var img_id = "img-" + stock_id;
////    	console.log(img_url);
////    	
////    	
////    	$("#stock-charts").append("<div class='col-md-4 each-chart " + stock_id + "'> " +
////	    								"<div class='chart-img'> " +
////	    									"<img src=" + img_url + " class='img-responsive' id=" + img_id + "> " +
////	    								"</div>" +
////	    								"<div class='chart-name'>" +
////	    									"<p>" + stock_id + "</p> " +
////	    								"</div> " +
////    								"</div>");
////    	
////    	$("#" + img_id).error(function(){
////    		alert( "Handler for .error() called. " + "#"+ stock_id);
//////    		$("div").removeClass("." + stock_id);
////    	});    	
////    	console.log(img_id);
////    	
////        return false;
////    });
//    
////    $("#writeForm").on("submit", function() {
////    	window.ws.send(JSON.stringify("write"));
////    	window.location = "/";
////        return false;
////    });
////    
////    $("#readBtn").click(function(){
//////    	$("#readDiv").slideToggle("slow");
////    	$("#readWispDiv").slideToggle("slow");
////    });
////    
////    $("#writeBtn").click(function(){
//////    	$("#writeDiv").slideToggle("slow");
////    	$("#writeWispDiv").slideToggle("slow");
////    });
//    
////    $('#stock-input-auto').keyup(function(){
////	      $.ajax({
////	    	  type: "POST",
////		      url: "/getAuto",
////		      data: JSON.stringify({'keyword' : $(this).val()}),
////		      contentType: 'application/json;charset=UTF-8',
////		      success: function (data) {
////		    	  console.log(data);
////		      }
////	  })    	
////    });
//    
//    
////    $('#stock-input-auto').typeahead({
////        source: function (query, result) {
////        	console.log(query);
////            $.ajax({
////                url: "http://stock.kakao.com/api/search/autocomplete.json",
////				data: 'keyword=' + query,            
////                dataType: "json",
////                type: "POST",
////                success: function (data) {
////					result($.map(data, function (item) {
////						return item;
////                    }));
////                }
////            });
////        }
////    });
//    
//});

function getStockImg(info){
  	stock_id = info.id;
  	stock_name = info.value;
  	stock_code = info.displayedCode;
  	
  	$.ajax({
    	  type: "POST",
	      url: "/getCurrentValue",
	      data: JSON.stringify(info),
	      contentType: 'application/json;charset=UTF-8',
	      success: function (data) {
	    	  	if (data == "End") {
	    	  		window.location.href = '/';
	    	  	}
	    	  	else
    	  		{
	    	  		$("#stock-charts").append(data);
	    	  		
	    	  		var offset = $("."+info.id).offset();
	    	  		console.log(info.id);
	    	  		console.log(offset);
	    	  		$('html, body').animate({scrollTop:offset.top}, 400);
	    	  		
	    	  		$(".form-control").val('');
	    	  		$(".form-control").blur();
	    	  		
    	  		}
//				$("#" + info.id).error(function(){
//					$("div").removeClass("." + stock_id);
//				});    	
	      }
   })
}

function logout(){
	$.ajax({
		  type: "POST",
	      url: "/logout",
	      success: function (data) {
	    	  window.location.href = '/';
	      }
	})
}


function changeChartType(param){
	
	$(".img-responsive").each(function(){
		if (param.id == 'day'){
			this.src = this.src.replace(/candle\/d?w?m?/, 'candle/d');
			this.style = "border: 1px solid #666666";
		}else if (param.id == 'week'){
			this.src = this.src.replace(/candle\/d?w?m?/, 'candle/w');
//			this.style = "border: 1px solid #C9302C";
			this.style = "border: 1px solid red";
		}else if (param.id == 'month'){
			this.src = this.src.replace(/candle\/d?w?m?/, 'candle/m');
//			this.style = "border: 1px solid #285F90";
			this.style = "border: 1px solid blue";
		}
	});
	
}

function deleteStockImg(param){
	$.ajax({
		  type: "POST",
	      url: "/deleteChartImage",
	      data: JSON.stringify({'id' : param.value, 'user' : 'admin'}) ,
	      contentType: 'application/json;charset=UTF-8',
	      success: function (data) {
	    	  console.log("." + param.value)
	    	  $("." + param.value).remove();
	      }
	})
}

$( function() {
	  $( "#stock-input-auto" ).autocomplete({
		  triggerSelectOnValidInput: false,
		  source: function( request, response ) {
		      $.ajax({
			    	  type: "POST",
				      url: "/getAuto",
				      data: JSON.stringify({'keyword' : request.term}),
				      contentType: 'application/json;charset=UTF-8',
				      success: function (data) {
				    	  response($.map(data, function(v, i){
				    		  return{
//				    			  label : v.displayedCode + " " + v.name + "          " + v.displayedSubtype,
				    			  label : v.displayedCode + "  " + v.name,
				    		  	  value : v.name,
				    		  	  id : v.code,
				    		  	  displayedCode : v.displayedCode,
				    		  	  assetId : v.assetId
				    		  };
				    	  }));
				      }
			   })
		  },
		  minLength: 1,
		  focus: function (event, ui){
			  return false;
		  },
		  select: function (event, ui) {
			  getStockImg(ui.item);
		  },
//		  close: function(){
//			  $(this).val("");

//			  $("#day-chart").focus();
//			  alert("test");
//		  }
	  });
});  
