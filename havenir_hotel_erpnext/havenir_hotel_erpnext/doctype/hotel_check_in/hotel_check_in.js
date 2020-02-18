// Copyright (c) 2020, Havenir and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hotel Check In", {
  setup: function(frm) {
    // setting query for rooms to be visible in list
    frm.set_query('room_no','rooms', function (doc){
      return{
        filters: {
          room_status: 'Available'
        }
      }
    });
  },
  
  guest_id: function(frm){
    var image_html = '<img src="' + frm.doc.guest_photo_attachment + '">';
    $(frm.fields_dict['guest_photo'].wrapper).html(image_html);
    frm.refresh_field('guest_photo');
  },
  
  refresh: function(frm){  
    var image_html = '<img src="' + frm.doc.guest_photo_attachment + '">';
    $(frm.fields_dict['guest_photo'].wrapper).html(image_html);
    frm.refresh_field('guest_photo');
  },

  validate: function(frm){
    for (var i in frm.doc.rooms){
      if (frm.doc.rooms[i].male == 0 && frm.doc.rooms[i].female == 0){
        frappe.throw('Please Enter Guests Details for Room ' + frm.doc.rooms[i].room_no);
      }
    }
  },

  total_amount: function(frm){
    var temp_total_amount = 0;
    for (var i in frm.doc.rooms){
      if (frm.doc.rooms[i].price){
        temp_total_amount += frm.doc.rooms[i].price;
      }
    }
    frm.doc.total_amount = temp_total_amount;
    frm.refresh_field('total_amount');
  }
});

frappe.ui.form.on('Hotel Check In Room', {
  room_no: function(frm, cdt, cdn) {
    let count = 0;
    let row = frappe.get_doc(cdt, cdn)
    if (row.room_no){
      for(var i in frm.doc.rooms){
        if (frm.doc.rooms[i].room_no == row.room_no){
          count += 1;
        }
      }
      if (count>1){
        let alert = 'Room ' + row.room_no + ' already selected';
        row.room_no = undefined;
        row.room_type = undefined;
        row.price = undefined;
        frm.refresh_field('rooms')
        frappe.throw(alert)
      }
      else {
        frm.call('get_room_price',{room: row.room_no}).then( r => {
          row.price = r.message;
          frm.refresh_field('rooms')
        })
      }
    }
    // frm.trigger('total_amount');
  },

  rooms_remove: function(frm) {
    // frm.trigger('total_amount');
  }
})
