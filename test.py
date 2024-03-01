import wx
import math
from os.path import join


class Entity:
    def __init__(self, x, y, text):
        self.x = int(x)
        self.y = int(y)
        self.text = text 
        self.width = 100 
        self.height = 50


class DiagramPanel(wx.Panel):
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_FULL_REPAINT_ON_RESIZE):
        super(DiagramPanel, self).__init__(parent, id, pos, size, style)
        self.objects = []
        self.SetDoubleBuffered(True)
        self.selected = None
        self.drag_start = None  
        self.relation_start = None  
        self.relationships = []  
        self.hovered = None 
        self.ctrl_hovered = None
        self.creating=()
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_MOTION, self.on_motion)

    def on_paint(self, event):
        
        dc = wx.BufferedPaintDC(self)
        
        dc.SetBackground(wx.Brush(wx.WHITE))
        dc.Clear()
        # 1. Draw Entities
        
        for obj in self.objects:
            if 1:
                if obj in [ self.hovered, self.ctrl_hovered]:  # Add this condition
                    #distances = [abs(self.mouse_point - edge) for edge in obj.edges]
                    dc.SetPen(wx.Pen(wx.BLACK, 3))  # Change edge thickness
                else:
                    dc.SetPen(wx.Pen(wx.BLACK, 1))  # Default edge thickness             
            dc.DrawRectangle(obj.x, obj.y, obj.width, obj.height)  # Draw the bounding box
            dc.DrawText(obj.text, obj.x + 5, obj.y + 5)  # Draw the entity label
            dc.SetPen(wx.Pen(wx.BLACK, 1))
        # 2. Draw Relationships
        for start_entity, end_entity, closest_edge, start_x, start_y, end_x, end_y, target_closest_edge in self.relationships:
            if start_entity and end_entity: 
                dc.DrawLine(start_x, start_y, end_x, end_y)

                # 3. (Optional) Draw an arrowhead at the end of the line
                self.draw_arrowhead(dc, end_x, end_y, start_x, start_y)
        if 1:
            # 3. Draw temporary line during relationship creation (if needed)
            #print('mid line', self.selected , self.drag_start) 
            if self.creating: 
                if 0:
                    if self.closest_edge == 'top':
                        start_x = self.selected.x + self.selected.width // 2
                        start_y = self.selected.y
                    elif self.closest_edge == 'bottom':
                        start_x = self.selected.x + self.selected.width // 2
                        start_y = self.selected.y + self.selected.height
                    elif self.closest_edge == 'left':
                        start_x = self.selected.x
                        start_y = self.selected.y + self.selected.height // 2
                    elif self.closest_edge == 'right':
                        start_x = self.selected.x + self.selected.width
                        start_y = self.selected.y + self.selected.height // 2

                #print('creating in on_paint', self.creating, self.closest_edge, self.selected.x, self.selected.y)
                dc.DrawLine(self.start_x, self.start_y, *self.creating)

    
    def draw_arrowhead(self, dc, x1, y1, x2, y2):
        arrow_length = 10  # Length of the arrowhead
        arrow_angle = 30  # Angle (in degrees) of the arrowhead

        # Calculate the angle of the line (in radians)
        line_angle = math.atan2(y1 - y2, x1 - x2)

        # Calculate the angles of the two sides of the arrowhead (in radians)
        angle1 = line_angle + math.radians(arrow_angle / 2)
        angle2 = line_angle - math.radians(arrow_angle / 2)

        # Calculate the coordinates of the two points that form the arrowhead
        x3 = x1 - arrow_length * math.cos(angle1)
        y3 = y1 - arrow_length * math.sin(angle1)
        x4 = x1 - arrow_length * math.cos(angle2)
        y4 = y1 - arrow_length * math.sin(angle2)

        # Draw the arrowhead
        dc.DrawPolygon([(x1, y1), (x3, y3), (x4, y4)])


    def on_left_down(self, event):
        pos = event.GetPosition()
        # Iterate over objects to find the one under the cursor
        for obj in reversed(self.objects): 
            if obj.x <= int(pos.x) <= obj.x + obj.width and obj.y <= int(pos.y) <= obj.y + obj.height: 
                if not event.ControlDown():  
                    # Normal selection: Set the clicked object as the selected one
                    self.selected = obj
                    #print('sel', self.selected)
                else:
                    # Relationship Creation
                    self.relation_start = obj  # Store the object as the start of the relationship

                    # Determine closest edge of the source object
                    x_dist_top = abs(pos.y - self.relation_start.y)
                    x_dist_bottom = abs(pos.y - (self.relation_start.y + self.relation_start.height))
                    y_dist_left = abs(pos.x - self.relation_start.x)
                    y_dist_right = abs(pos.x - (self.relation_start.x + self.relation_start.width))

                    closest_edge = None
                    min_distance = min(x_dist_top, x_dist_bottom, y_dist_left, y_dist_right)

                    if min_distance == x_dist_top:
                        closest_edge = 'top'
                    elif min_distance == x_dist_bottom:
                        closest_edge = 'bottom'
                    elif min_distance == y_dist_left:
                        closest_edge = 'left'
                    elif min_distance == y_dist_right:
                        closest_edge = 'right'

                    # Calculate the middle point of the closest edge
                    if closest_edge == 'top':
                        self.start_x = obj.x + obj.width // 2
                        self.start_y = obj.y 

                    elif closest_edge == 'bottom':
                        self.start_x = obj.x + obj.width // 2
                        self.start_y = obj.y + obj.height 

                    elif closest_edge == 'left':
                        self.start_x = obj.x  
                        self.start_y = obj.y + obj.height // 2

                    elif closest_edge == 'right':
                        self.start_x = obj.x + obj.width 
                        self.start_y = obj.y + obj.height // 2
                    #print('on_left_down',closest_edge)
                    # Store other relevant information
                    self.closest_edge = closest_edge

                self.drag_start = pos 
                break  # Exit the loop since an object was found


        if 0:
            print('relation_start:', self.relation_start)
            print('selected:', self.selected)
            print('drag_start:', self.drag_start)

            
    def on_left_up(self, event):
        pos = event.GetPosition()  
        self.creating=()
        # Iterate over objects to find the one under the cursor
        for obj in reversed(self.objects): 
            if obj.x <= int(pos.x) <= obj.x + obj.width and obj.y <= int(pos.y) <= obj.y + obj.height: 
                if not event.ControlDown():  
                    # Normal selection: Set the clicked object as the selected one
                    self.selected = obj
                else:
                    # Relationship Creation
                    end_entity = obj  # Store the object as the end of the relationship
                    if self.relation_start != end_entity:  # Avoid self-loops

                        # Determine nearest edge of the target entity
                        target_pos = event.GetPosition()  
                        x_dist_top = abs(target_pos.y - end_entity.y)
                        x_dist_bottom = abs(target_pos.y - (end_entity.y + end_entity.height))
                        y_dist_left = abs(target_pos.x - end_entity.x)
                        y_dist_right = abs(target_pos.x - (end_entity.x + end_entity.width))

                        target_closest_edge = None
                        min_distance = min(x_dist_top, x_dist_bottom, y_dist_left, y_dist_right)

                        if min_distance == x_dist_top:
                            target_closest_edge = 'top'
                        elif min_distance == x_dist_bottom:
                            target_closest_edge = 'bottom'
                        elif min_distance == y_dist_left:
                            target_closest_edge = 'left'
                        elif min_distance == y_dist_right:
                            target_closest_edge = 'right'

                        # Calculate the midpoint of the target's nearest edge
                        if target_closest_edge == 'top':
                            end_x = end_entity.x + end_entity.width // 2
                            end_y = end_entity.y
                        elif target_closest_edge == 'bottom':
                            end_x = end_entity.x + end_entity.width // 2
                            end_y = end_entity.y + end_entity.height
                        elif target_closest_edge == 'left':
                            end_x = end_entity.x
                            end_y = end_entity.y + end_entity.height // 2
                        elif target_closest_edge == 'right':
                            end_x = end_entity.x + end_entity.width
                            end_y = end_entity.y + end_entity.height // 2
                        #print(self.closest_edge, target_closest_edge)
                        # Store relationship information
                        self.relationships.append((self.relation_start, end_entity, self.closest_edge, self.start_x, self.start_y, end_x, end_y, target_closest_edge))
                        self.relation_start = None  
                        self.Refresh()  
                break # Exit the loop since an object was found

        self.drag_start = None  

 
 


    def on_motion(self, event):
        self.mouse_point = event.GetPosition()
        pos = event.GetPosition()
        if 1:
                
            self.hovered = None 
            self.ctrl_hovered = None 
            for obj in reversed(self.objects): 
                if obj.x <= int(pos.x) <= obj.x + obj.width and obj.y <= int(pos.y) <= obj.y + obj.height: 
                    # Set hovered object
                    #print('set', obj)
                    if not self.drag_start:
                        self.hovered = obj
                        self.selected=obj
                    else:
                        if event.ControlDown():
                            #print('setting ctrl hovered')
                            self.ctrl_hovered = obj
                    break
                else:
                    pass
                    #print('passed', obj)
            #self.Refresh() 
        if self.drag_start:
            

            if self.selected and self.drag_start:


                dx = pos.x - self.drag_start.x
                dy = pos.y - self.drag_start.y

                if event.ControlDown():  # Relationship Creation Mode
                    #print('dragging/creating', self.selected, self.drag_start, event.ControlDown())
                    # Visual Feedback for Relationship Creation (Example)
                    temp_end_x, temp_end_y = pos  # Get temporary endpoint for drawing
                    self.creating=(temp_end_x, temp_end_y)

                    #self.Refresh()  # Redraw to show a temporary line

                else:  # Normal Object Dragging Mode
                    #print('dragging/obf', self.selected, self.drag_start, event.ControlDown())
                    self.selected.x += dx
                    self.selected.y += dy

                    # Update Relationship Coordinates
                    for i, (start_entity, end_entity, closest_edge, start_x, start_y, end_x, end_y, target_closest_edge) in enumerate(self.relationships):
                        if start_entity == self.selected:
                            if closest_edge == 'top':
                                start_x = self.selected.x + self.selected.width // 2
                                start_y = self.selected.y
                            elif closest_edge == 'bottom':
                                start_x = self.selected.x + self.selected.width // 2
                                start_y = self.selected.y + self.selected.height
                            elif closest_edge == 'left':
                                start_x = self.selected.x
                                start_y = self.selected.y + self.selected.height // 2
                            elif closest_edge == 'right':
                                start_x = self.selected.x + self.selected.width
                                start_y = self.selected.y + self.selected.height // 2
                            self.relationships[i] = (start_entity, end_entity, closest_edge, start_x, start_y, end_x, end_y, target_closest_edge)

                        elif end_entity == self.selected:
                            if closest_edge in ( 'bottom'):
                                end_x = self.selected.x + self.selected.width // 2
                                end_y = self.selected.y 
                            if closest_edge in ('top', ):
                                end_x = self.selected.x + self.selected.width // 2
                                end_y = self.selected.y + self.selected.height                            
                            elif closest_edge in ( 'right'):
                                end_y = self.selected.y + self.selected.height // 2
                                end_x = self.selected.x 
                            elif closest_edge in ('left'):
                                end_x = self.selected.x + self.selected.width
                                end_y = self.selected.y + self.selected.height // 2                            
                            self.relationships[i] = (start_entity, end_entity, closest_edge, start_x, start_y, end_x, end_y, target_closest_edge)

                self.drag_start = pos
        self.Freeze()
        self.Refresh()  # Force a redraw
        self.Thaw()


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.panel = DiagramPanel(self) 
        self.objects = self.panel.objects 

        self.objects.append(Entity(50, 50, "Entity 1"))
        self.objects.append(Entity(200, 120, "Entity 2"))

        self.create_toolbar()

        sizer = wx.BoxSizer(wx.VERTICAL)  
        sizer.Add(self.panel, 1, wx.EXPAND)  
        self.SetSizer(sizer)

    def create_toolbar(self):
        toolbar = self.CreateToolBar()
        add_tool = toolbar.AddTool(wx.ID_ANY, "Add Entity", wx.Bitmap(join('images',"add_icon.png"))) 
        self.Bind(wx.EVT_TOOL, self.on_add_entity, add_tool)

        toolbar.Realize()

    def on_add_entity(self, event):
        text = wx.GetTextFromUser("Enter entity name:", "New Entity")
        if text:
            new_entity = Entity(10, 10, text) 
            self.objects.append(new_entity)
            self.panel.Refresh() 

if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame(None, title="ER Diagram Builder", size=(600,600))
    frame.Show()
    app.MainLoop()
