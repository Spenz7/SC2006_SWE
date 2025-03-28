/** 
  * Template Name: Home Property
  * Version: 1.0  
  * Template Scripts
  * Author: MarkUps
  * Author URI: http://www.markups.io/

  Custom JS
  

  1. FIXED NAVBAR 
  2. AGENTS SLIDER
  3. TESTIMONIAL SLIDER  
  4. CLIENT BRAND SLIDER (SLICK SLIDER)
  5. TOP SLIDER (SLICK SLIDER)
  6. LATEST PRODUCT SLIDER (SLICK SLIDER)
  7. HOVER DROPDOWN MENU
  8. ADVANCE SEARCH FILTER  (noUiSlider SLIDER)
  9. MIXIT FILTER ( FOR GALLERY ) 
  10. FANCYBOX ( FOR PORTFOLIO POPUP VIEW )
  11. SCROLL TOP BUTTON
  12. PRELOADER
  13. GRID AND LIST LAYOUT CHANGER 
  14.RELATED ITEM SLIDER (SLICK SLIDER)

  
**/

jQuery(function($){


  /* ----------------------------------------------------------- */
  /*  1. FIXED NAVBAR 
  /* ----------------------------------------------------------- */
    
    
  jQuery(window).bind('scroll', function () {
    if (jQuery(window).scrollTop() > 200) {
        jQuery('.main-navbar').addClass('navbar-fixed-top');
        
      } else {
          jQuery('.main-navbar').removeClass('navbar-fixed-top');          
      }
  });
  
  /* ----------------------------------------------------------- */
  /*  2. AGENTS SLIDER
  /* ----------------------------------------------------------- */    

    jQuery('.aa-agents-slider').slick({
      dots: false,
      arrows: false,
      infinite: true,
      speed: 300,
      slidesToShow: 4,
      slidesToScroll: 1,
      autoplay: true,
      autoplaySpeed: 2500,
      responsive: [
        {
          breakpoint: 1024,
          settings: {
            slidesToShow: 3,
            slidesToScroll: 3,
            infinite: true,
            dots: true
          }
        },
        {
          breakpoint: 600,
          settings: {
            slidesToShow: 2,
            slidesToScroll: 2
          }
        },
        {
          breakpoint: 480,
          settings: {
            slidesToShow: 1,
            slidesToScroll: 1
          }
        }
        // You can unslick at a given breakpoint now by adding:
        // settings: "unslick"
        // instead of a settings object
      ]
    });

  /* ----------------------------------------------------------- */
  /*  3. TESTIMONIAL SLIDER 
  /* ----------------------------------------------------------- */    

    jQuery('.aa-testimonial-slider').slick({
        dots: false,      
        infinite: true,
        speed: 500,      
        cssEase: 'linear'
      });

  /* ----------------------------------------------------------- */
  /*  4. CLIENT BRAND SLIDER (SLICK SLIDER)
  /* ----------------------------------------------------------- */  

   jQuery('.aa-client-brand-slider').slick({
      dots: false,
      arrows: false,
      infinite: true,
      speed: 300,
      slidesToShow: 5,
      slidesToScroll: 1,
      autoplay: true,
      autoplaySpeed: 2500,
      responsive: [
        {
          breakpoint: 1024,
          settings: {
            slidesToShow: 4,
            slidesToScroll: 4,
            infinite: true,
            dots: true
          }
        },
        {
          breakpoint: 600,
          settings: {
            slidesToShow: 2,
            slidesToScroll: 2
          }
        },
        {
          breakpoint: 480,
          settings: {
            slidesToShow: 1,
            slidesToScroll: 1
          }
        }
        // You can unslick at a given breakpoint now by adding:
        // settings: "unslick"
        // instead of a settings object
      ]
    });

  
  /* ----------------------------------------------------------- */
  /*  5. TOP SLIDER (SLICK SLIDER)
  /* ----------------------------------------------------------- */    

    jQuery('.aa-top-slider').slick({
      dots: false,
      infinite: true,
      arrows: true,
      speed: 500,
      fade: true,
      cssEase: 'linear'
    });
    
  /* ----------------------------------------------------------- */
  /*  6. LATEST PRODUCT SLIDER (SLICK SLIDER)
  /* ----------------------------------------------------------- */      

    jQuery('.aa-properties-details-img').slick({
      dots: false,
      infinite: true,
      arrows: true,
      speed: 500,      
      cssEase: 'linear'
    });

      
  /* ----------------------------------------------------------- */
  /*  7. HOVER DROPDOWN MENU
  /* ----------------------------------------------------------- */ 
  
  // for hover dropdown menu
    jQuery('ul.nav li.dropdown').hover(function() {
      jQuery(this).find('.dropdown-menu').stop(true, true).delay(200).fadeIn(200);
    }, function() {
      jQuery(this).find('.dropdown-menu').stop(true, true).delay(200).fadeOut(200);
    });

 
  /* ----------------------------------------------------------- */
  /* 8. ADVANCE SEARCH FILTER  (noUiSlider SLIDER)
  /* ----------------------------------------------------------- */        

    jQuery(function(){
      if(jQuery('body').is('.aa-price-range')){
        // FOR AREA SECTION
       // FOR AREA SECTION
      var skipSlider = document.getElementById('aa-sqrfeet-range');
      if (skipSlider) {
        noUiSlider.create(skipSlider, {
          range: {
            'min': 0,
            'max': 1000
          },
          snap: false,
          step: 10,
          connect: true,
          start: [0, 1000]
        });

        var skipValues = [
          document.getElementById('skip-value-lower'),
          document.getElementById('skip-value-upper')
        ];

        skipSlider.noUiSlider.on('update', function (values, handle) {
          if (skipValues[handle]) {
            skipValues[handle].innerHTML = values[handle];
          }
        });
      }

      // FOR PRICE SECTION
      var skipSlider2 = document.getElementById('aa-price-range');
      if (skipSlider2) {
        noUiSlider.create(skipSlider2, {
          range: {
            'min': 0,
            'max': 5000000
          },
          step: 10000,
          connect: true,
          start: [0, 6000000]
        });

        var skipValues2 = [
          document.getElementById('skip-value-lower2'),
          document.getElementById('skip-value-upper2')
        ];

        skipSlider2.noUiSlider.on('update', function (values, handle) {
          if (skipValues2[handle]) {
            skipValues2[handle].innerHTML = values[handle];
          }
        });
}

  /* ----------------------------------------------------------- */
  /*  9. MIXIT FILTER ( FOR GALLERY ) 
  /* ----------------------------------------------------------- */  

    jQuery(function(){
      jQuery('#mixit-container').mixItUp();
    });

  /* ----------------------------------------------------------- */
  /*  10. FANCYBOX ( FOR PORTFOLIO POPUP VIEW ) 
  /* ----------------------------------------------------------- */ 
      
    jQuery(document).ready(function() {
      jQuery(".fancybox").fancybox();
    });  
   
    
  /* ----------------------------------------------------------- */
  /*  11. SCROLL TOP BUTTON
  /* ----------------------------------------------------------- */

  //Check to see if the window is top if not then display button

    jQuery(window).scroll(function(){
      if (jQuery(this).scrollTop() > 300) {
        jQuery('.scrollToTop').fadeIn();
      } else {
        jQuery('.scrollToTop').fadeOut();
      }
    });
     
    //Click event to scroll to top

    jQuery('.scrollToTop').click(function(){
      jQuery('html, body').animate({scrollTop : 0},800);
      return false;
    });
  
  /* ----------------------------------------------------------- */
  /*  12. PRELOADER
  /* ----------------------------------------------------------- */

   jQuery(window).load(function() { // makes sure the whole site is loaded      
      jQuery('#aa-preloader-area').delay(300).fadeOut('slow'); // will fade out      
    })
   


  /* ----------------------------------------------------------- */
  /*  13. GRID AND LIST LAYOUT CHANGER 
  /* ----------------------------------------------------------- */

  jQuery("#aa-list-properties").click(function(e){
    e.preventDefault(e);
    jQuery(".aa-properties-nav").addClass("aa-list-view");
  });
  jQuery("#aa-grid-properties").click(function(e){
    e.preventDefault(e);
    jQuery(".aa-properties-nav").removeClass("aa-list-view");
  });


  /* ----------------------------------------------------------- */
  /*  14. RELATED ITEM SLIDER (SLICK SLIDER)
  /* ----------------------------------------------------------- */      

    jQuery('.aa-related-item-slider').slick({
      dots: false,
      infinite: false,
      speed: 300,
      slidesToShow: 4,
      slidesToScroll: 4,
      responsive: [
        {
          breakpoint: 1024,
          settings: {
            slidesToShow: 3,
            slidesToScroll: 3,
            infinite: true,
            dots: true
          }
        },
        {
          breakpoint: 600,
          settings: {
            slidesToShow: 2,
            slidesToScroll: 2
          }
        },
        {
          breakpoint: 480,
          settings: {
            slidesToShow: 1,
            slidesToScroll: 1
          }
        }
        // You can unslick at a given breakpoint now by adding:
        // settings: "unslick"
        // instead of a settings object
      ]
    }); 

    function loadPropertyDetails(propertyId) {
      $.ajax({
          url: `/get_property_details/${propertyId}`,  
          type: 'GET',
          success: function(data) {
              if (data.error) {
                  alert(data.error);
                  return;
              }
  
              // Load property details into modal
              $('#modal-flat-type').text(data.property.flat_type);
              $('#modal-town').text(data.property.town);
              $('#modal-street-name').text(data.property.street_name);
              $('#modal-floor-area').text(data.property.floor_area);
              $('#modal-max-com-bid').text(data.property.max_com_bid);
              $('#modal-years-remaining').text(data.property.years_remaining);
              $('#modal-listing-price').text(data.property.listing_price);
  
              // Clear existing rows in the table
              $('#bidder-list').empty();
  
              if (data.bidders.length > 0) {
                  data.bidders.forEach(bidder => {
                      $('#bidder-list').append(`
                          <tr>
                              <td>${bidder.bidder_username}</td>
                              <td>$${bidder.bid_amount}</td>
                              <td>${bidder.review}</td>
                          </tr>
                      `);
                  });
              } else {
                  $('#bidder-list').append(`
                      <tr>
                          <td colspan="3" class="text-center">No bids yet</td>
                      </tr>
                  `);
              }
  
              // Show the modal
              $('#propertyModal').modal('show');
          },
          error: function() {
              alert("Failed to load property details. Please try again.");
          }
      });
  }
  window.loadPropertyDetails = loadPropertyDetails;

}
});
 
});
