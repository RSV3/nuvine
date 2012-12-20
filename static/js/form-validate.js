$(function(){
	 $(".form-validate").validationEngine('attach');
            
		// This method is called right before the ajax form validation request
		// it is typically used to setup some visuals ("Please wait...");
		// you may return a false to stop the request 
		function beforeCall(form, options){
			if (window.console) 
			console.log("Right before the AJAX form validation call");
			return true;
		}
            
		// Called once the server replies to the ajax form validation request
		function ajaxValidationCallback(status, form, json, options){
			console.log("well i got here");
			if (window.console) 
			console.log(status);
                
			if (status === true) {
				var action = $('#form-action').val();
				console.log(action);
				$(".form-validate-ajax").attr('action',action);
				form.validationEngine('detach');
				form.submit();
			}
		}
            
		
			$(".form-validate-ajax").validationEngine({
				ajaxFormValidation: true,
				onAjaxFormComplete: ajaxValidationCallback,
			});

  });		