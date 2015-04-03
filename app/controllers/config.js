import Ember from "ember";
import ENV from "../config/environment";


var Timezones=Ember.A([{id:1,region:"Africa",zones:["Abidjan","Accra","Addis Ababa","Algiers","Asmara","Asmera","Bamako","Bangui","Banjul","Bissau","Blantyre","Brazzaville","Bujumbura","Cairo","Casablanca","Ceuta","Conakry","Dakar","Dar es Salaam","Djibouti","Douala","El Aaiun","Freetown","Gaborone","Harare","Johannesburg","Juba","Kampala","Khartoum","Kigali","Kinshasa","Lagos","Libreville","Lome","Luanda","Lubumbashi","Lusaka","Malabo","Maputo","Maseru","Mbabane","Mogadishu","Monrovia","Nairobi","Ndjamena","Niamey","Nouakchott","Ouagadougou","Porto-Novo","Sao Tome","Timbuktu","Tripoli","Tunis","Windhoek"]},{id:2,region:"America",zones:["Adak","Anchorage","Anguilla","Antigua","Araguaina","Argentina","Aruba","Asuncion","Atikokan","Atka","Bahia","Bahia Banderas","Barbados","Belem","Belize","Blanc-Sablon","Boa Vista","Bogota","Boise","Buenos Aires","Cambridge Bay","Campo Grande","Cancun","Caracas","Catamarca","Cayenne","Cayman","Chicago","Chihuahua","Coral Harbour","Cordoba","Costa Rica","Creston","Cuiaba","Curacao","Danmarkshavn","Dawson","Dawson Creek","Denver","Detroit","Dominica","Edmonton","Eirunepe","El Salvador","Ensenada","Fortaleza","Fort Wayne","Glace Bay","Godthab","Goose Bay","Grand Turk","Grenada","Guadeloupe","Guatemala","Guayaquil","Guyana","Halifax","Havana","Hermosillo","Indiana","Indianapolis","Inuvik","Iqaluit","Jamaica","Jujuy","Juneau","Kentucky","Knox IN","Kralendijk","La Paz","Lima","Los Angeles","Louisville","Lower Princes","Maceio","Managua","Manaus","Marigot","Martinique","Matamoros","Mazatlan","Mendoza","Menominee","Merida","Metlakatla","Mexico City","Miquelon","Moncton","Monterrey","Montevideo","Montreal","Montserrat","Nassau","New York","Nipigon","Nome","Noronha","North Dakota","Ojinaga","Panama","Pangnirtung","Paramaribo","Phoenix","Port-au-Prince","Porto Acre","Port of Spain","Porto Velho","Puerto Rico","Rainy River","Rankin Inlet","Recife","Regina","Resolute","Rio Branco","Rosario","Santa Isabel","Santarem","Santiago","Santo Domingo","Sao Paulo","Scoresbysund","Shiprock","Sitka","St Barthelemy","St Johns","St Kitts","St Lucia","St Thomas","St Vincent","Swift Current","Tegucigalpa","Thule","Thunder Bay","Tijuana","Toronto","Tortola","Vancouver","Virgin","Whitehorse","Winnipeg","Yakutat","Yellowknife"]},{id:3,region:"Antarctica",zones:["Casey","Davis","DumontDUrville","Macquarie","Mawson","McMurdo","Palmer","Rothera","South Pole","Syowa","Vostok"]},{id:4,region:"Arctic",zones:["Longyearbyen"]},{id:5,region:"Asia",zones:["Aden","Almaty","Amman","Anadyr","Aqtau","Aqtobe","Ashgabat","Ashkhabad","Baghdad","Bahrain","Baku","Bangkok","Beirut","Bishkek","Brunei","Calcutta","Choibalsan","Chongqing","Chungking","Colombo","Dacca","Damascus","Dhaka","Dili","Dubai","Dushanbe","Gaza","Harbin","Hebron","Ho Chi Minh","Hong Kong","Hovd","Irkutsk","Istanbul","Jakarta","Jayapura","Jerusalem","Kabul","Kamchatka","Karachi","Kashgar","Kathmandu","Katmandu","Khandyga","Kolkata","Krasnoyarsk","Kuala Lumpur","Kuching","Kuwait","Macao","Macau","Magadan","Makassar","Manila","Muscat","Nicosia","Novokuznetsk","Novosibirsk","Omsk","Oral","Phnom Penh","Pontianak","Pyongyang","Qatar","Qyzylorda","Rangoon","Riyadh","Riyadh87","Riyadh88","Riyadh89","Saigon","Sakhalin","Samarkand","Seoul","Shanghai","Singapore","Taipei","Tashkent","Tbilisi","Tehran","Tel Aviv","Thimbu","Thimpu","Tokyo","Ujung Pandang","Ulaanbaatar","Ulan Bator","Urumqi","Ust-Nera","Vientiane","Vladivostok","Yakutsk","Yekaterinburg","Yerevan"]},{id:6,region:"Atlantic",zones:["Azores","Bermuda","Canary","Cape Verde","Faeroe","Faroe","Jan Mayen","Madeira","Reykjavik","South Georgia","Stanley","St Helena"]},{id:7,region:"Australia",zones:["ACT","Adelaide","Brisbane","Broken Hill","Canberra","Currie","Darwin","Eucla","Hobart","LHI","Lindeman","Lord Howe","Melbourne","North","NSW","Perth","Queensland","South","Sydney","Tasmania","Victoria","West","Yancowinna"]},{id:8,region:"Brazil",zones:["Acre","DeNoronha","East","West"]},{id:9,region:"Canada",zones:["Atlantic","Central","Eastern","East-Saskatchewan","Mountain","Newfoundland","Pacific","Saskatchewan","Yukon"]},{id:10,region:"Chile",zones:["Continental","EasterIsland"]},{id:11,region:"Etc",zones:["GMT","GMT0","GMT-0","GMT+0","GMT-1","GMT+1","GMT-2","GMT+2","GMT-3","GMT+3","GMT-4","GMT+4","GMT-5","GMT+5","GMT-6","GMT+6","GMT-7","GMT+7","GMT-8","GMT+8","GMT-9","GMT+9","GMT-10","GMT+10","GMT-11","GMT+11","GMT-12","GMT+12","Greenwich","UCT","Universal","UTC","Zulu"]},{id:12,region:"Europe",zones:["Amsterdam","Andorra","Athens","Belfast","Belgrade","Berlin","Bratislava","Brussels","Bucharest","Budapest","Busingen","Chisinau","Copenhagen","Dublin","Gibraltar","Guernsey","Helsinki","Isle of Man","Istanbul","Jersey","Kaliningrad","Kiev","Lisbon","Ljubljana","London","Luxembourg","Madrid","Malta","Mariehamn","Minsk","Monaco","Moscow","Nicosia","Oslo","Paris","Podgorica","Prague","Riga","Rome","Samara","San Marino","Sarajevo","Simferopol","Skopje","Sofia","Stockholm","Tallinn","Tirane","Tiraspol","Uzhgorod","Vaduz","Vatican","Vienna","Vilnius","Volgograd","Warsaw","Zagreb","Zaporozhye","Zurich"]},{id:13,region:"GMT",zones:["GMT"]},{id:14,region:"Indian",zones:["Antananarivo","Chagos","Christmas","Cocos","Comoro","Kerguelen","Mahe","Maldives","Mauritius","Mayotte","Reunion"]},{id:15,region:"Mexico",zones:["BajaNorte","BajaSur","General"]},{id:16,region:"Mideast",zones:["Riyadh87","Riyadh88","Riyadh89"]},{id:17,region:"Pacific",zones:["Apia","Auckland","Chatham","Chuuk","Easter","Efate","Enderbury","Fakaofo","Fiji","Funafuti","Galapagos","Gambier","Guadalcanal","Guam","Honolulu","Johnston","Kiritimati","Kosrae","Kwajalein","Majuro","Marquesas","Midway","Nauru","Niue","Norfolk","Noumea","Pago Pago","Palau","Pitcairn","Pohnpei","Ponape","Port Moresby","Rarotonga","Saipan","Samoa","Tahiti","Tarawa","Tongatapu","Truk","Wake","Wallis","Yap"]},{id:18,region:"US",zones:["Alaska","Aleutian","Arizona","Central","Eastern","East-Indiana","Hawaii","Indiana-Starke","Michigan","Mountain","Pacific","Pacific-New","Samoa"]},{id:19,region:"UTC",zones:["UTC"]}]);

export default Ember.ObjectController.extend({
  timezones: Timezones,
  config: {},
  hostname: "",
  tzRegion: "",
  tzZone: "",
  tzZones: function() {
    var self = this;
    var tzo = Timezones.find(function(i) {
      return i.region.replace(" ", "_") == self.get('tzRegion');
    });
    if (tzo.region == "GMT" || tzo.region == "UTC") {
      return [tzo.region];
    } else {
      return tzo.zones;
    };
  }.property('tzRegion'),
  offset: function() {
    return this.get('model').datetime.datetime.offset.toFixed(2);
  }.property('model.datetime'),
  actions: {
    updateTime: function() {
      var self = this;
      $.ajax({
        url: ENV.APP.krakenHost+'/config/datetime',
        type: 'PUT',
        success: function(j) {
          self.get('model').timezone = j;
          self.message.success("Time updated successfully");
        },
        error: function(e) {
          if (e.status == 500) self.transitionToRoute("error", e);
        }
      });
    },
    save: function() {
      var self = this;
      $.ajax({
        url: ENV.APP.krakenHost+'/config',
        type: 'PUT',
        data: JSON.stringify({config: self.get('config')}),
        contentType: 'application/json',
        processData: false,
        error: function(e) {
          if (e.status == 500) self.transitionToRoute("error", e);
        }
      });
      $.ajax({
        url: ENV.APP.krakenHost+'/config/hostname',
        type: 'PUT',
        data: JSON.stringify({hostname: self.get('hostname')}),
        contentType: 'application/json',
        processData: false,
        error: function(e) {
          if (e.status == 500) self.transitionToRoute("error", e);
        }
      });
      $.ajax({
        url: ENV.APP.krakenHost+'/config/timezone',
        type: 'PUT',
        data: JSON.stringify({timezone: {region: self.get('tzRegion'), zone: self.get('tzZone').replace(" ", "_")}}),
        contentType: 'application/json',
        processData: false,
        error: function(e) {
          if (e.status == 500) self.transitionToRoute("error", e);
        }
      });
      self.message.success("System preferences saved successfully");
    }
  }
});
